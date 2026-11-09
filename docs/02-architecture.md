# 02 架构 · 对译 Duiyi Android

> 状态：当前（2026-11-10）｜真源：`app/src/main/java/com/duiyi/android/**` 与 `app/src/main/cpp/**`；本文是该代码的架构说明，冲突时以代码为准。
> 设计期架构（ML Kit / 系统识别器路线）已归档到 [`_archive/README.md`](_archive/README.md)，不作为现状。

目标：在 Android 上实现一个**可注册功能平台**——面对面 / 同声传译 / 会议记录共用任务、历史、模型准备与引擎边界，但各自拥有独立 ViewModel 与字幕状态，不互相塞逻辑。

## 1. 分层与目录

```
app/                 DuiyiApplication · AppBindings(Hilt) · MainActivity(NavHost) · FeatureRegistry · PreferencesStore · ForegroundActivity
designsystem/        Tokens · Components · DuiyiTheme（Compose）
domain/              AppLanguage · FeatureID · ServiceProtocols · CaptionModels · TaskSessionController
                     TranslationPolicy · DuiyiError · Copy · ManagedAssets
                     routing/ ClauseSplitter · SpokenSegmentJoiner · StablePrefixTracker · UtteranceAssembler
features/            home · conversation · interpretation · meeting · history · models · onboarding · shared
services/            speech · translation · tts · audio · persistence · summary · export · assets · permissions
                     ComputeGate · LatencyProbe · DuiyiLog
cpp/                 llama_jni.cpp（llama.cpp ⇄ Kotlin 的 JNI 桥）
```

| 层 | 可以 | 不可以 |
| --- | --- | --- |
| `app` | Hilt 组装、导航、全局偏好、模块注册 | 写字幕合并/切句规则 |
| `features` | Domain 协议 + DesignSystem；少量基础设施类型（`ComputeGate`、`LatencyProbe`、`TranslationPump`、`SpeechEngineException`、`SpeechIntentBridge`） | 直接持有 `SpeechRecognizer`/`AudioRecord`/`TextToSpeech` 实现类型（系统设置跳转经 `SpeechRecognizerFactory.fixIntent` 生成 Intent） |
| `domain` | Kotlin 数据类与纯函数 | import Android UI/系统语音/翻译/Room 类型（当前 `domain/` 无 `android.*` import） |
| `services` | Domain 协议 + Android 系统 API | import `features.*` 或引用任何 ViewModel（当前无反向依赖） |
| `designsystem` | Compose 视觉 | 业务状态机 |

Hilt 绑定集中在 `app/AppBindings.kt`：`TaskStore→RoomTaskStore`、`LanguageCataloging→DeviceLanguageCatalog`、`SpeechRecognizing→AndroidSpeechEngine`、`Translating→GemmaTranslator`、`SpeechSynthesizing→SystemSpeechSynthesizer`、`AudioSessionConfiguring→AudioSessionPolicy`、`PermissionGranting→PermissionService`、`DeviceCapabilityProbing→DeviceCapabilityProbe`、`ExportSharing→TranscriptExportService`、`ConversationSummarizing→HonestSummarizer`。Room 数据库由 `DatabaseModule` 提供。

## 2. 导航与生命周期

- `MainActivity` 用一个 `NavHost`，路由：`onboarding → home → conversation / interpretation / meeting / models / history → history detail(taskId)`；竖屏锁定。
- 首页用 `FeatureRegistry.visible` 渲染模块卡（面对面 / 同传 / 会议），历史卡单独加；新模块 = `FeatureID` 加 case + `FeatureID.route` + `FeatureRegistry` 登记 + Feature 目录 + 路由分支。
- 进行中任务时，返回/离开模块走确认（`BackHandler` + 对话框）；切模块或进后台只停听写，不结束任务（`PauseOnStop`）。
- 全局 Hilt 单例存活于进程：`GemmaTranslator` 等模型句柄由服务层持有，界面销毁不卸载模型。

## 3. 任务与会话控制

- 数据模型：`TaskSession`（`ServiceProtocols.kt`）含 `TaskStatus`（`Running | PausedListening | Ended`）、语言对、`TranscriptEntry`、`ConversationSummary`。
- 状态操作全部经 `domain/TaskSessionController`：`restore()` / `beginNew()` / `persist()` / `setListening()` / `saveSummary()` / `finish()`；ViewModel 不直接拼 `TaskStore` 调用顺序。
- `finish()`：先 `append` 最后一次内存字幕；若没有任何非空源文则 `delete`（空任务不进历史），否则 `end` 并让任务从 active 列表消失。
- 会话的「听写状态」由 ViewModel 的 `SessionState`（`Idle / Preparing / Ready / Listening / Paused / Failed`）驱动；**暂停只把 `TaskStatus` 改为 `PausedListening` 并停麦克风**，不触达结束。
- 杀进程后 `restore()` 从 `TaskStore.activeTask(feature)` 取回未结束任务并回放字幕。

## 4. 监听状态与字幕模型

- `domain/CaptionModels.kt`：`CaptionLine(id, side, source, sourceText, translatedText, phase)`，`phase ∈ {Streaming, Settled}`；`PaneState(history, live, speakingHint)` 是现场字幕状态机。
- `PaneState` 的关键操作：`applyLive()`（新 live 或按 `SpokenText.isContinuation` 合并）、`applyTranslation()`（更新 live/历史行译文，`settle` 决定是否置为 Settled）、`archiveLive()`、`absorbRefinement()`（吸收后续 refinement，历史窗口 `HISTORY_LIMIT = 40`）。
- **实时字幕以内存为准**：`PaneState` 是 UI 事实源；`TranscriptEntry` 只在 settled/暂停/结束时异步落盘。面对面两个 `PaneState`（user/peer，上屏倒置），同传/会议各一个。
- 语种路由在 `domain/routing/LanguageRouter`（`targetSide` / `targetLanguage`）；面对面据识别语种决定译文写哪一侧，同传/会议单向。

## 5. 持久化

- Room：数据库 `duiyi.db`，实体 `TaskEntity` + `TranscriptEntity`（`RoomStore.kt`），`schemaVersion = 1`、`exportSchema = false`；`RoomTaskStore` 实现 `TaskStore` 并负责 Domain↔Entity 映射。
- 进行中任务的字幕先写内存，按 250 ms debounce 批量 `append`；暂停/结束/进后台再强制 flush。`append()` 当前实现是**删除该任务全部 entries 后全量重写**（已知性能问题，见 05），不是增量写。
- 历史详情只读；不把现场 `CaptionLine`/`PaneState` 状态机复用到历史页。

## 6. 并发与算力协调

- 协程：ViewModel 用 `viewModelScope` + `StateFlow`；识别/解码/翻译在 `Dispatchers.Default`，落盘/IO 在 `Dispatchers.IO`。
- **同一时刻只有一个听写会话**：引擎内部用 generation/token 使旧流失效；切模块先 `stop()` 再 `start()`。
- **翻译单工人队列** `TranslationPump`：`LinkedHashMap<utteranceId, job>` 保存 pending（同句重提覆盖 pending），后台单协程逐条执行；**已开始的生成不取消**（避免半截译文），队列空时才会跑投机 prefill。
- **`ComputeGate`**：进程级「大核正在生成」标志；Genma 生成期间，听写侧跳过 partial 重解码（final 不跳），保证生成不被抢核。默认开启，可在调试页运行时切换做 A/B。
- 大核绑定：`cpp/llama_jni.cpp` 的 `pin_to_big_cores` 在模型加载与 decode 前按 `cpu_capacity` 降序取前 n 个核，用 `sched_setaffinity` 把 JNI 线程绑上去（ggml 工作线程继承）；线程数取 `min(4, max(2, CPU 核数))`。真机核占用与延迟数字见 07/08。
- 诊断：`LatencyProbe` 记录一轮「VAD→解码→排队→首字→生成→应用」；`DuiyiLog` 写文件日志；`SpeechProbe` 记录语音启动。

## 7. 引擎边界

| 边界 | 实现 | 说明 |
| --- | --- | --- |
| 听写 `SpeechRecognizing` | `AndroidSpeechEngine` | 按厂商分叉：荣耀/华为 → `SherpaSpeech`；其他 → 系统 `SpeechRecognizer`（`callbackFlow` 包装、候选服务排序、重启与 watchdog） |
| 端侧听写 | `SherpaSpeech` + `sherpa-onnx` | `AudioRecord` 16 kHz → Silero VAD → SenseVoice int8 `OfflineRecognizer`（final 整段 + 每秒 partial）→ `SpokenSegmentJoiner`/`UtteranceAssembler` |
| 翻译 `Translating` | `GemmaTranslator` | 进程级 Hilt 单例；`Mutex` 串行化句柄与生成；`prepare()` 加载 GGUF + 按语言对预热前缀 KV；`translate()` 拼前缀/后文并生成；`release()` 卸载 |
| 翻译队列 | `TranslationPump` | 单工人 FIFO；只译 final（默认）；同句覆盖 pending；管理投机 prefill/`ComputeGate` |
| 原生推理 | `LlamaNative` + `cpp/llama_jni.cpp` | `create/warmPrefix/generate/progress/prefillSource/abort/destroy`；Q4_K_M GGUF、KV 前缀槽、abort 回调 |
| TTS | `SystemSpeechSynthesizer` | 系统 `TextToSpeech`；队列上限 2、按增量后缀朗读、耳机/听筒门禁在 ViewModel 侧判断 |
| 音频 | `AudioSessionPolicy` | 耳机/听筒检测（`AudioDeviceCallback`）供同传读出使用；三档 use case 当前均 `MODE_NORMAL`（桩，见 05） |
| 总结 | `HonestSummarizer` | 桩：`availability()` 恒 `DeviceNotEligible`，`summarize()` 直接报错（见 05） |

## 8. 模型管理

- SenseVoice：`SherpaModelStore` 管理三件（`model.int8.onnx` ≈239 MB、`tokens.txt`、`silero_vad.onnx`），多镜像下载（hf-mirror → HuggingFace → ModelScope），阈值 `minBytes` 判定完成；仅在荣耀/华为机型的听写路径必需。
- TranslateGemma：`GemmaModelStore` 管理 `translategemma-4b-it.Q4_K_M.gguf`（预期 ≈2.49 GB，`MIN_BYTES` 2 GB），多镜像；翻译路径必需。
- 下载：`RemoteFileDownloader` 支持 HTTP `Range` 断点续传与镜像回退；`DeviceAssetCatalog` 聚合进度/占用给 UI。
- 模型准备时机：引导页下载；点「听」时 `prepare()`（加载 + 语言对前缀预热）；会议入口 `release()` 卸载 4B；失败/缺失时以 `DuiyiError` 提示并给下载入口。

## 9. 错误模型

- 统一枚举 `domain/DuiyiError`（麦克风被拒、模型缺失、设备不支持、识别中断/静默、Google 麦克风被拒、荣耀默认识别器阻断、译文未就绪、无朗读声、无 GMS 等），`userMessage(language)` 按六语给出**原因 + 下一步**文案。
- 服务层用 `SpeechEngineException` 包装底层异常，ViewModel 用 `SpeechEngineException.of()` 归一为 `DuiyiError`；UI 只在字幕/操作区展示错误，不解析错误码。
- 错误可附带修复 Intent（如跳系统语音设置/给 Google 授权）；**没有「静默改走云」分支**。

## 10. 构建边界

- `minSdk 34` / `compileSdk 35` / `targetSdk 35`，仅 `arm64-v8a`；Kotlin + Compose + Hilt + Room + NDK/CMake（llama.cpp、sherpa-onnx）。
- Gradle wrapper 固定在 8.10.2，Gradle JDK 用 17–21（不要用 Android Studio 自带 JDK 25）；`duiyiArmArch` 是 Gradle 属性，默认 `armv8.2-a+dotprod`（`armv8.6-a+dotprod+i8mm` 实测更慢，见 08）。
- 旧设计名对照：`AppEnvironment` → 现为 `DuiyiApplication` + `AppBindings`；`LanguageCatalog` → `LanguageCataloging` + `DeviceLanguageCatalog`；`DuiyiNavHost` → `MainActivity` 里的 `NavHost`。`TaskSession` 仍是 `ServiceProtocols.kt` 的当前数据模型。
