# 04 运行时 · 对译 Duiyi Android

> 状态：当前（2026-11-10）｜真源：`app/src/main/java/com/duiyi/android/**`；延迟/模型数字口径见 [`07-on-device-llm.md`](07-on-device-llm.md) 与 [`08-latency.md`](08-latency.md)。

本文讲「从麦克风 PCM 到屏幕字幕 / 耳机朗读 / 本地历史」的运行时路径，不重复目录结构（见 02）。

## 1. 总流水线

```
AudioRecord 16 kHz ──► Silero VAD 端点
                         ├─ final 段 ──► SenseVoice 整段离线解码 ─┐
                         └─ 每 1 s partial 快照 ──► SenseVoice 解码 ─┤
                                                                    ▼
                                             SpokenSegmentJoiner（HOLD 1.4 s）
                                                        │
                                            UtteranceAssembler（语种锁/脚本校验）
                                                        │
                                    语种路由（面对面）/ 单向（同传、会议）
                                                        │
                                   TranslationPump（默认只译 final；可选增量）
                                                        │
                                       TranslateGemma（llama.cpp，前缀 KV 复用）
                                                        │
                                   内存字幕 PaneState ──► Compose 字幕 / 可选 TTS
                                                        │
                                          250 ms debounce ──► Room（结束/暂停时 flush）
```

**结构性延迟**：VAD 端点（0.55 s）→ 整段 ASR → 整句 LLM 三层串行；默认不做「边听边译」，这是延迟的主要来源（分析与方案见 08）。

## 2. 音频采集与 VAD

- `AudioRecord`：16 kHz、单声道、PCM 16-bit；音频源按 `VOICE_RECOGNITION → MIC → UNPROCESSED` 依次尝试，全部失败报麦克风错误。
- 环形缓冲 8 s（`SampleAccumulator`，16 000 × 8 samples），供 partial/final 重解码。
- Silero VAD 参数（`SherpaSpeech.createVad`）：`threshold=0.5`、`minSilenceDuration=0.55 s`、`minSpeechDuration=0.35 s`、`maxSpeechDuration=20 s`、窗口 512、`numThreads=1`。
- 每段语音结束（静音 ≥0.55 s 或到 20 s 上限）产出一个 final 段；partial 以约 1 s 节奏产出，用于刷新 live 原文。

## 3. 听写解码

- 荣耀/华为：`sherpa-onnx` SenseVoice int8 `OfflineRecognizer` 离线整段解码；模型含中/英/日/韩/粤的 `lang` 标签，路由以标签 + 脚本推断为主（系统语言检测回调不参与荣耀路径）。
- 其他厂商：系统 `SpeechRecognizer` 路径（候选服务排序、重启/watchdog 在 `AndroidSpeechEngine`），行为与荣耀路径共用 `Utterance` 出口。
- partial 解码受 `ComputeGate` 约束：**生成翻译期间跳过 partial 重解码**（`skipPartialsWhileTranslating` 默认开），final 永不跳过；跳过次数由延迟探针记录。

## 4. 切句、拼装与语种路由

- `SpokenSegmentJoiner`：像句子的片段（`TranslationPolicy.isSentenceLike` 或 `isPacked`）立即释放；不像句子的短句先攒着，最多 **`HOLD_NS = 1.4 s`** 后由 `tick()` 释放。`tick()` 由解码循环内的 200 ms ticker 驱动，**不依赖「有解码发生」**（否则短句要等下一句才出译文，见 05）。语言变化时强制 flush。
- `UtteranceAssembler`：按语种锁（`lockedLanguage`）与脚本校验过滤串音；同句 continuation/refinement 不换 `utteranceId`；切换语种时开新句。
- 面对面路由：`LanguageRouter.targetSide(detected, userLanguage)` 决定译文写 user 屏还是 peer 屏；`SpokenText.scriptIsDecisive` 用于脚本可判定时纠正语种。1 s 串扰窗口内抑制另一侧抢话。
- 单向场景（同传：源语 → 我听的语言；会议：只记录）不经过双向路由。

## 5. 翻译泵（TranslationPump）

- **默认只译 final**：partial 只用来刷新原文并触发「投机 prefill」（在队列空闲时把当前 partial 对应的源句前缀解码进 KV，final 到达时只补增量）。
- **增量翻译（`incrementalTranslation`，默认关）**：按稳定前缀（`StablePrefixTracker`）切稳定子句，逐段翻译并**追加**；不修改已上屏内容。默认关的原因是片段脱离上下文会掉质量。
- 队列语义：单工人、`LinkedHashMap<utteranceId, job>` 保存 pending（同句重提覆盖未开始的 pending）；**已开始的生成不取消**；同语言直接回原文；结果在 `Dispatchers.Main.immediate` 应用到字幕。
- 生成：llama.cpp 贪心解码；`prepare()` 时对每个语言对预热前缀 KV；生成时若 speculative prefill 命中，复用 KV 只补后缀；180 s 超时 abort；输出经 `TranslateGemmaPrompt.sanitize` 清洗。
- 进度的 `inProgressText()` 每 120 ms 轮询，把生成中的文本流式回显到字幕（不落盘，只有 final 才落盘）。

## 6. TTS（同声传译）

- 只在同声传译模块可用；`voiceOutEnabled` 默认关。开启时要求已接**耳机/听筒**（`AudioSessionPolicy.currentRoute().canSpeakWithoutEcho`），只走扬声器时禁止并提示「请戴上耳机再读出」；拔出耳机即时停止朗读并关闭开关。
- 队列上限 `SPEECH_QUEUE_LIMIT = 2`；按**增量后缀**朗读（新句若以上一句为前缀，只读新增部分）。
- 系统 `TextToSpeech`：`AUDIOFOCUS_GAIN_TRANSIENT_MAY_DUCK`、`USAGE_MEDIA/SPEECH`、语速 1.08、单句 12 s 超时；无该语言声时关闭读出并报「无朗读声」。

## 7. 落盘

- **内存是实时字幕真源**：`PaneState` 更新即 UI 更新；`TranscriptEntry` 只在 settled、暂停、结束、进后台时提交落盘。
- ViewModel 用 `schedulePersist()`：`TranslationPolicy.PERSIST_MS = 250 ms` 去抖后调用 `TaskStore.append`；结束时 flush 最后一遍。
- `RoomTaskStore.append` 当前是「删该任务全部 entries + 全量插回」（已知写放大，见 05），不是增量写。
- 相机/切后台只暂停听写，不做后台服务续听；杀进程后从 Room 恢复未结束任务。

## 8. 模型准备

- 引导页：荣耀机型下载 SenseVoice（约 240 MB）+ TranslateGemma 4B（约 2.49 GB）；其他机型只下载翻译模型。模型下载支持多镜像与断点续传（见 02 §8）。
- 点「听」：先 `audioSession.activate(...)`，再 `translator.prepare(语言对双向)`（加载 4B + 逐对预热前缀），Voice 模型在 `SherpaSpeech.prepare()` 内按需加载；准备完成才置 `Listening`。
- 会议记录入口：`translator.release()` 卸载 4B，把内存/核让给听写；再次需要翻译时按需重新加载。
- 失败/缺失模型：`DuiyiError.ModelsMissing` / `SpeechModelsMissing`，文案带大小与下载入口。

## 9. 并发与抢核

- 协程与线程：UI 主线程；解码/翻译在 `Dispatchers.Default`；下载/落盘在 `Dispatchers.IO`。
- **同刻一个听写会话**：`stop()` 使旧 flow 的 generation 失效，切模块先停再起。
- **同刻一个翻译生成**：`GemmaTranslator` 的 `Mutex` + `TranslationPump` 单工人保证顺序；`ComputeGate` 让听写知道「大核正在生成」并跳过 partial。
- llama.cpp 线程数 `min(4, max(2, CPU 核数))`；JNI `pin_to_big_cores` 按 `cpu_capacity` 降序绑前 n 个大核（`sched_setaffinity`，ggml 工作线程继承），把 SenseVoice partial 解码和 Gemma 生成放在同一批大核上竞争。Q4 内核与抢核实测见 07/08。
- 诊断：`LatencyProbe`（一轮分解：VAD 端点 / 解码 / joiner 持有 / 排队 / 首字 / 生成 / 总计）、`DuiyiLog`（文件日志）、`SpeechProbe`（语音启动与自检）；调试入口仅开发用（收敛计划见 05）。

## 10. 关键可调参数（代码常量/偏好）

| 参数 | 默认值 | 位置 / 说明 |
| --- | --- | --- |
| VAD 静音窗 | `0.55 s`（`minSilenceDuration`） | 端点延迟主要来源；面对面可评估单独调短（见 08） |
| VAD 最短语音 / 最长段 | `0.35 s` / `20 s` | 超长段强制切分 |
| partial 节奏 | 约 `1 s` | `SherpaSpeech` 的 `PARTIAL_NS` |
| 短句持有 | `HOLD_NS = 1.4 s` | `SpokenSegmentJoiner`；ticker 200 ms |
| 落盘去抖 | `PERSIST_MS = 250 ms` | `TranslationPolicy` |
| 串扰窗口 | `1 s` | `CROSSTALK_WINDOW_MS` |
| 同传朗读队列 | `2` 句 | `SPEECH_QUEUE_LIMIT` |
| 会议正文上限 | `20 000` 字符 | `MEETING_TRANSCRIPT_LIMIT` |
| 增量翻译 | 关 | `PreferencesStore.incrementalTranslation` |
| ARM 编译参数 | `armv8.2-a+dotprod` | Gradle 属性 `duiyiArmArch`（i8mm 变体实测更慢，见 08） |
| 大核绑定 | 前 n 个 `cpu_capacity` 最高的核 | `llama_jni.cpp` 的 `pin_to_big_cores`（`sched_setaffinity`；n = 线程数） |

## 11. 错误到文案

- 服务层抛 `SpeechEngineException(DuiyiError)` 或返回空译文；ViewModel 用 `SpeechEngineException.of()` 归一到 `DuiyiError`。
- UI 通过 `DuiyiError.userMessage(language)` 展示六语文案（原因 + 下一步），并可按需附带修复 Intent（系统语音设置、Google 应用授权等）。
- 已知语义：`RecognitionInterrupted` 提示可继续；`TranslationUnavailable` 表示「听清了但译文未就绪」；`VoiceOutNeedsHeadphones` 提示戴耳机；任何环境/能力问题都不得伪造成成功。
