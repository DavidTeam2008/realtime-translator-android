# 08 延迟：端到端归因、优化状态与测量方法

> 本文是**当前技术资产**：回答「译文为什么慢、慢在哪、下一步怎么测」。数字均标注测量日期与设备；无法回溯的标「历史记录，未复测」。
> 相关：端侧模型细节见 [`07-on-device-llm.md`](07-on-device-llm.md)；运行时流水线见 [`04-runtime.md`](04-runtime.md)；选型与不做清单见 [`03-decisions.md`](03-decisions.md)；现状缺陷见 [`09-current-state.md`](09-current-state.md)；后续排期见 [`06-roadmap.md`](06-roadmap.md)；索引见 [`README.md`](README.md)。

## 1. 结论摘要

- 面对面端到端当前口径 **约 2–2.7 s**（`09-current-state` 的现状描述；Honor ALP-AN00，2026-09；**非** n 轮中位数采样）。
- 慢的一半在 **Gemma**（源句 prefill + 自回归生成 ≈ 0.9–2.0 s），另一半在 **VAD 端点 + 整段 ASR + joiner 缓冲 + 串行排队**；这是三层串行的结构性结果，不是单点。
- 最大的未知数是**抢核**：SenseVoice 的 partial 解码每秒重解整段累积音频、和 Gemma 抢同一批大核。`ComputeGate` 与延迟探针已就绪，但**真实对话的探针数据从未采集**。
- 因此下一步不是继续调内核或 VAD 参数，而是**先跑一轮探针把预算测出来**，再决定改什么。

## 2. 端到端结构（三层串行）

```text
麦克风 → Silero VAD（静音 0.55 s 切段） → SenseVoice 整段解码（final）
      → SpokenSegmentJoiner（HOLD 1.4 s，等句子像） → 语种/脚本路由
      → TranslationPump（单 worker 串行） → TranslateGemma 4B（prefill + greedy 生成）
      → 字幕 / 可选 TTS
```

串行性的来源不是实现偷懒，而是每一层都缺「边听边出」的能力：

1. **VAD 必须先判定说完**（`minSilenceDuration = 0.55 s`），否则不知道句子边界；
2. **SenseVoice 对整段累积音频解码**，没有流式增量输出，final 之前只有会抖动的 partial；
3. **LLM 只对 final 生成**（现默认只译 final；增量分段是可选开关），一次生成 0.5–1.7 s。

任何一层想「提前」，都要么牺牲质量（partial 重译乱跳，已证伪），要么改流水线结构（增量分段/流式回字幕）。

## 3. 延迟预算（面对面，一次 3 s 中文句）

| 阶段 | 估算/实测 | 依据与状态 |
| --- | --- | --- |
| 说话（示例 3 s） | 3000 ms | 不可压缩（只为对齐口径） |
| VAD 端点静音 | **550 ms** | `SherpaSpeech` 的 `minSilenceDuration = 0.55f`；代码常量 |
| SenseVoice 整段解码 | 150–450 ms（估算） | RTF × 语音时长；**从未实测**（探针有 `final_decode`/`final_rtf` 字段，待采集） |
| Joiner 缓冲 | **0 或 ≥1400 ms** | `SpokenSegmentJoiner.HOLD_NS = 1.4 s`；句子像/带标点立即放行，短句要等超时（D-1 已修，见 §5） |
| 翻译排队 | 0–1700 ms（估算） | `TranslationPump` 单 worker FIFO；in-flight 生成不取消 |
| Gemma 源句 prefill | 300–600 ms | 自检实测 373 ms（2026-09-07，Honor ALP-AN00） |
| Gemma 生成 | 500–1400 ms | 自检实测 `gen_ms` 670 ms（短句）；整句 1717 ms 的长输出例见 §4 |
| **合计** | **约 1.5–3.0 s（估算）** | 与现状口径 2–2.7 s 一致 |

> 这张表是**预算模型**，不是一次对话的实测分解：除 VAD 550 ms 与 Gemma 两项外，其余为估算。真实分解必须用 §7 的探针采集。

## 4. 现状数字（标注日期/设备）

**端到端**：面对面约 **2–2.7 s**（`09-current-state`，Honor ALP-AN00 / 骁龙 8+ Gen 1 / Android 14，2026-09 口径；未记录 n、未记录分位）。这是「最大体验问题」，也是本文件的优化对象。

**隔离自检**（`TranslationSelfTestActivity`，2026-09-07，Honor ALP-AN00，**历史记录，未复测**）：

| 步骤 | 耗时 | 拆分 |
| --- | --- | --- |
| `prepare`（加载 + 双向前缀预热） | 18049 ms | 加载约 8–11 s + 每方向约 3 s |
| en→zh `How are you.` | 1075 ms | `prefix 15` + `suffix 373` + `gen 670` |
| en→zh `It's very cute.` | 1145 ms | 短句 |
| zh→en `这个也不对呀。` | 1717 ms | 英文输出更长，decode 更久 |

**口径警告**：自检没有麦克风、没有 VAD、没有并发 SenseVoice，只测 Gemma 本身；**不能把它当端到端延迟**，也不能用它与 §3 的预算直接相加或比较（真实路径会更慢）。

## 5. 已实施优化与结论

| # | 优化 | 现状 | 结论/代价 |
| --- | --- | --- | --- |
| 0 | 前缀 KV 快照（语言对级） | 已实现，2026-09 自检验证命中 15–19 ms | 短句从约 3.7 s 降到约 1.1 s（历史记录）；点「听」多付一次预热 |
| 1 | 大核绑定（4 线程绑 X2+A710） | 已实现，2026-09 自检验证 | 只改变调度不改算法；替 SenseVoice 时仍会互相拖慢 |
| 2 | **D-1 joiner 卡死修复** | 已实现（200 ms ticker 并入 decode 循环的 `select`），**待真机验证** | 短句松口后约 1.4 s 内出译文；`joiner_hold` 应稳定在 1400 ms 附近 |
| 3 | 流式回字幕 | 已实现（JNI 逐 token 更新 progress + 120 ms 轮询，只更新 UI 不写库） | 总时长不变，首字可提前上屏；真机观感待确认 |
| 4 | **ComputeGate**（生成期跳过 partial 解码） | 已实现，默认开，调试页可运行时切换做 A/B | 换来 Gemma 不被抢核；代价是另一侧实时原文短暂停更（≤ 一次生成） |
| 5 | **投机 prefill**（`prefillSource`） | 已实现（独立 speculative 槽 + pump 空闲自门控） | 预期省源句 prefill 的大部分；**收益未实测**，失配即回退不更慢 |
| 6 | ARM 内核 i8mm / Q4_K 8×8 | **已否决**（保留 `-PduiyiArmArch` 开关） | 生成慢 8–31%、整句慢 24%，默认保持 dotprod；复现见 `07-on-device-llm` |
| 7 | 增量分段翻译 | 已实现，`incrementalTranslation` **默认关** | 只追加不覆盖，长句可提前 1–3 s 看到首句译文；片段脱离上下文，质量需真机 A/B |
| 8 | 专用小模型分流 | **未做** | 唯一可能带来量级提升的方向，但无手机 CPU 实测数据，先 A/B 再决定 |
| 9 | D-2 长句等说完 | **未修**（结构性） | 只译 final 导致连续 15 s 无译文；增量分段是缓解方案，不是修复 |

### 两个刻意的取舍

- **ComputeGate 默认开**：生成期间不重解 partial，避免和 Gemma 抢核；代价是 live 原文短暂停更。它可运行时关闭，正是为了让 A/B 能测出「抢核到底值多少」。
- **增量翻译默认关**：质量风险（片段脱离上下文）高于确定收益，先作为可选项、等真机 A/B。

## 6. 明确不做的

- 再加线程 / 用小核（只有 4 个大核，屏障会让情况更糟）；
- OpenCL / Hexagon（内核适配与稳定性成本远超收益）；
- 换 12B / FP16（更准但更慢，同传不可用）；
- 把上一句塞回 prompt（4B 会译成 `[背景]` 并串台，已实证）；
- 对 partial 做全量重译（译文乱跳，已回退）；
- 只调 VAD 静音窗或 `HOLD_NS` 来「优化」——在拿到探针数据前调这些参数只是换一种体感，不是修归因。

## 7. 测量方法（真机、可复现）

**入口**：调试页 `LatencyDebugActivity`，显示每次翻译的中位数与最近 12 轮明细；页面顶部开关可切换「生成期间跳过 partial 解码」，用于同一场对话内做 A/B。

```bash
# 1) 启动调试页（包名固定，不写本机路径）
adb shell am start -n com.duiyi.android/.debug.LatencyDebugActivity
# 2) 正常面对面聊 8–10 轮中英（同一组句子/脚本，减少方差）
# 3) 拉取原始记录（应用私有 files 目录下的 latency-probe.txt）
adb pull /data/data/com.duiyi.android/files/latency-probe.txt
```

`latency-probe.txt` 每轮一行、`key=value` 可解析；内存中保留最近 40 轮，文件超过 256 KB 时只留尾部。字段含义：

| 字段 | 含义 |
| --- | --- |
| `speech_to_endpoint` | 从最后一个语音块到 VAD 判端点的时长（预期≈550 ms） |
| `audio` | 本轮参与解码的音频时长 |
| `final_decode` / `final_rtf` | SenseVoice 整段解码耗时 / 实时率（音频毫秒 ÷ 解码毫秒） |
| `partial_decode` / `partials` | 最近一次 partial 解码耗时 / 本轮 partial 次数 |
| `partials_during_gen` | 与 Gemma 生成重叠的 partial 次数（**抢核指标**） |
| `partials_skipped` | 被 ComputeGate 跳过的 partial 次数 |
| `joiner_hold` | 从 ingest 到 flush 的持有时间（D-1 是否修好） |
| `queue_wait` / `queued_behind` | 翻译排到 worker 前的等待 / 提交时前面有几条 |
| `first_token` | 从开始翻译到第一个 token 上屏 |
| `gen` / `out_chars` | 生成耗时 / 输出字符数 |
| `speech_to_done` | 从最后一个语音块到译文落屏的端到端总时长 |

**口径要求**：

1. 同一设备、同一组句子、屏幕常亮、尽量安静；至少 **8–10 轮**，看**中位数**，不看单轮。
2. 抢核必须测**两轮**：调试页开关「开」一轮、「关」一轮（每次切换会清空记录），对比 `gen` 中位数与 `partials_during_gen`；差值才是 ComputeGate 的价值。
3. 不要把探针数字与 `TranslationSelfTestActivity` 的隔离自检混用：自检无并发、无 VAD，系统性更乐观。
4. 探针的端到端锚点是「最后一个语音块」，不是「开口时刻」；讨论「用户体感」时要说明这一点。

## 8. 下一步

1. **先测预算**：跑 §7 的两轮 A/B，拿到 `speech_to_endpoint` / `final_decode` / `joiner_hold` / `gen` 的真实中位数，以及抢核量级。这是后续所有调参的前提。
2. **确认 D-1 修复**：短句（「好的」「Thank you」）松口后应在约 1.4 s 内出译文，`joiner_hold` 稳定在 1400 ms 附近；不达标按缺陷处理，不调 `HOLD_NS` 掩盖。
3. **确认流式观感**：看 `first_token` 是否明显早于 `gen`；总时长不变，属于体感优化。
4. **增量翻译 A/B**：同一段长句对比「首句译文出现时间」与「可读性」；质量退化明显就保持默认关。见 [`06-roadmap.md`](06-roadmap.md) 的 Next 列表。
5. **再考虑模型分层**：以上都做完仍不够快，才评估「短句走专用小模型、长句走 4B」的分流；必须用真实对话同时测延迟与可读性（选型见 [`03-decisions.md`](03-decisions.md)，候选与许可证风险见 [`07-on-device-llm.md`](07-on-device-llm.md)）。

## 9. 未验证与风险

- **真实对话的探针数据尚未采集**（2026-11-10 时点）：`08` 原归档写于 2026-09/11，探针代码在树但从未在真机跑过一段对话；因此上面所有「抢核」「D-1 已修」「投机收益」都只是代码就绪，不是实测结论。
- **端到端 2–2.7 s 没有采样记录**：口径、n、分位均未记录，只能作为历史现状描述。
- **SenseVoice 的 `final_decode` / RTF 从未实测**：预算表里 150–450 ms 是估算。
- **i8mm 结论样本有限**：每组 3 轮、`gen_ms` 波动约 ±20%，结论依赖长输出档与总量方向；复测需受控热状态。
- **只在 Honor ALP-AN00 验证**：其他 SoC 的绑核布局、大小核能力与 i8mm 支持未验证。
- **与 iOS 不可直接对比**：两端流水线（听写引擎、VAD、翻译会话）不同，跨平台比延迟需要单独口径。
