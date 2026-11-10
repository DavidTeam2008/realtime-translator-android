# 05 已知问题与底线 · Android

> 状态：当前规范（问题清单 + 验收底线）。最后核对：2026-11-10（对照当前工作树代码，未提交视为待修）。
> 状态口径：`已修`（代码已改，注明提交或批次） / `待修`（尚未有修复） / `未验证`（方案未定或无法本机验证）。
> harness 改造批次（P2–P5，见 [`06-roadmap.md`](06-roadmap.md)）期间清洁项并行处理；**修复后必须回来更新本表状态与证据**，不要只改代码。
> 决策背景见 [`03-decisions.md`](03-decisions.md)；延迟专项见 [`08-latency.md`](08-latency.md)；设备验证范围见本页第 4 节。

## 1. 已确认缺陷（D-1 – D-6）

| ID | 问题 | 影响 | 代码证据 | 状态 | 处置建议 |
| --- | --- | --- | --- | --- | --- |
| D-1 | 短句攒句后「永远不翻译」，要等下一句说话才出译文 | 高（短句体验） | 原 `SherpaSpeech` 解码循环只把 `tick()` 放在解码之后；现行已加 200 ms ticker 进 `select` | **已修**（代码已含 `TICK_MS=200` 的 ticker；待真机复验） | 真机用延迟探针确认 `joiner_hold` 稳定在约 1400 ms |
| D-2 | 只译 final：长句要说完整句才出译文 | 高（核心体验） | `ConversationViewModel.enqueueTranslation()` / `InterpretationViewModel.enqueueTranslation()` 的 `if (!isFinal) return`；增量翻译默认关 | **待修**（设计选择，缺陷仍在） | 流式回字幕 + 增量分段翻译 A/B（默认关）后再定默认 |
| D-3 | 模型文件用 `minBytes` 判完成：80 MB 就当作 239 MB 的模型就绪 | 中（截断模型到推理期才报错） | `SherpaModelSpec.isComplete()` 为 `size >= part.minBytes`；`model.int8.onnx` 的 `minBytes = 80_000_000` | **待修** | 按期望字节数或校验和判定；下载完成再做一次完整性校验 |
| D-4 | 每次落盘重写整张字幕表：删光该任务全部行再全量插回 | 中（长会议 O(n²) 写放大） | `RoomStore.append()`：`dao.deleteEntries(taskId)` 后 `upsertEntries(...)`；约每 250 ms 触发（`TranslationPolicy.PERSIST_MS`） | **待修** | 改为增量插入 / 差量写，或按 taskId 分段事务 |
| D-5 | 诊断文件无上限、无轮转 | 低（长期占空间） | `DuiyiLog` 追加写 `duiyi.log`；`SpeechProbe` 追加写 `speech-probe.txt`，均无大小上限 | **待修** | 大小 / 天数轮转 + 总量上限；探针默认降噪 |
| D-6 | 工程卫生项（见下方分项） | 中（构建可复现性与发布卫生） | 见下方分项 | **部分已修 / 其余待修** | P3 清洁批次逐项处理 |

### D-6 分项状态（2026-11-10 工作树核对）

| 分项 | 现状 | 状态 |
| --- | --- | --- |
| `app/.cxx/` 编译中间产物入库 | 已停止跟踪（提交 `7b27087`，早于本次改造） | 已修 |
| `prototype/platform.html` 留在根目录 | 已归档到 `_archive/prototype/`（P1，2026-11-10） | 已修 |
| `third_party/llama.cpp` 是绝对路径符号链接 | 已删除入库的绝对符号链接；`CMakeLists.txt` 固定 tag `b10775` 走 `FetchContent`，本机可用 `LLAMA_CPP_SRC` 指向本地源码（不入库） | 已修（P3，2026-11-10） |
| debug Activity 留在 release 包且 `exported=true` | 两个调试入口已移入 `app/src/debug/`（debug manifest overlay），release 变体不合并；`adb ... .debug.*` 仅对 debug 包有效 | 已修（P3，2026-11-10） |
| 死代码 | 已删除：4 个未引用节流常量、`InterpretationViewModel.debounceJobs`、`Copy.translationPackBody`、`ManagedAssets.indeterminate` 及其 UI 分支（测试同步移除构造参数） | 已修（P3，2026-11-10；单测 PASS） |
| `gradlew.local.sh` 入库且含本机绝对路径 | 已迁为 `scripts/gradlew-local.sh`：路径改从 `ANDROID_HOME`/`JAVA_HOME`/`local.properties` 读取，不再含机器路径 | 已修（P3，2026-11-10） |
| `.gitignore` 缺常见项 | 已补 `.kotlin/`、`*.hprof`、`captures/` | 已修（P3，2026-11-10） |
| 代码质量存量债 | detekt/ktlint/Android Lint 已有 findings 写入三份 baseline（`app/*-baseline.xml`）；新增问题会让 `make check-quality` 失败 | 记录（P4，2026-11-10） |

### D-1 / D-2 补充说明

- **D-1**：单测 `SpokenSegmentJoinerTest.timeoutFlushesHeldShort` 一直是绿的，但它直接调 `tick()`，测不到「调用点不存在」。修复的关键不是 `tick()` 本身，而是让 ticker 独立于解码循环；真机复验看 `joiner_hold`（目标约 1400 ms）与「不带标点短句松口后 1.4 s 内出译文」。
- **D-2**：当前代码在非 final 路径上只做投机 prefill（不产出译文），所以默认行为仍是「连续说 15 秒、屏幕 15 秒没有译文」。`incrementalTranslation` 默认 false（`PreferencesStore`），打开后才按稳定前缀分段追加翻译；它是实验开关，不是默认体验。
- **订正（2026-11-10）**：旧现状文（`_archive/2026-11/09-current-state.md`）称「`ConversationViewModel` 里 summarize-and-save 是死代码」；按当前工作树核对，四个模块都有总结入口且 `requestSummary()` 已接线，功能不可用的原因是 `HonestSummarizer` 桩恒返回 `DeviceNotEligible`，**不是死代码**。以本页为准。

## 2. 桩代码与产品呈现（三选一建议）

原则：桩要么实现，要么从 UI 撤掉，要么明确标「未验证 / 部分设备可用」——不允许让用户以为是 bug。

| 桩 | 现状（类型 / 行为） | 产品呈现 | 建议 | 理由 |
| --- | --- | --- | --- | --- |
| 会后总结 | `HonestSummarizer.availability()` 恒 `DeviceNotEligible`；`summarize()` 直接抛错 | 面对面 / 同传 / 会议 / 历史都有「总结」入口，点击弹出「本机不可用」说明 | **撤 UI 或标未验证**（二者择一；有 AICore 真机后再实现） | 绝大多数设备恒不可用，保留入口容易被读成 bug；若保留，文案必须写「部分设备可本机生成，其余请导出」 |
| 音频会话策略 | `AudioSessionPolicy.activate()` 三个 `AudioUseCase` 分支完全同构（都是 `MODE_NORMAL`）；同传读出没有切 `MODE_IN_COMMUNICATION`，AEC 未生效 | 无直接 UI；用户感知是「戴耳机读出时 AEC 效果未知」 | **实现（小改动）或标未验证** | 分支与场景语义已存在，补 `MODE_IN_COMMUNICATION` / `isSpeakerphoneOn` 的区分成本低；不实现则文档不得声称「分场景音频策略」 |
| 语言能力目录 | `DeviceCapabilityProbe` 的 `installedSpeechLocales` / `supportedSpeechLocales` 恒为空集；`DeviceLanguageCatalog` 按 provider 退化 | 选语种时能力灰置可能不准（尤其泰 / 越与日语 / 韩语） | **实现探测 或 标未验证** | 探测 API 可用时应填真值（`checkRecognitionSupport` / 端侧语言列表），并保留当前退化作为兜底 |
| 按语言对下载 / 删除 | `DeviceAssetCatalog.downloadLanguage()` / `deleteLanguage()` 写死 `English`；实际是单 4B 覆盖全语对 | Models 页只有一张翻译模型卡 | **撤接口（推荐）** | 单模型策略下不存在「按语言对管理」，残留方法是死代码且误导后续维护 |

> 建议的落地顺序：先撤「总结 / 按语言对下载」的误导性入口，再补「音频策略」小实现，语言能力探测随后（需要真机核对灰置结果）。

## 3. 取舍与妥协（当前仍成立）

- **非荣耀设备路径**：代码在，但无真机验证（Pixel / 三星 / 无端侧识别机）。不得对外承诺与荣耀同质量。
- **Android 没有系统双引擎**：同一时刻只有一个 `SpeechRecognizer`，面对面靠单引擎多语种切换 + 文本路由，抢话 / 快速换语言会丢词或错屏；这是平台限制，不是实现偷懒。
- **会议记录是单语**：只转写不翻译（与 iOS v1 一致），进入会议会卸载 4B 释放内存，回到面对面需要重新准备（约 18 s 量级）。
- **远场听写弱**：OEM 识别器多为近讲训练，桌面平放时对面方向更差；产品只能提示摆位，不承诺降噪。
- **TTS 与蓝牙**：TTS 引擎质量因厂商而异；蓝牙 SCO 下读出与识别可能互相影响，失败时保字幕、关读出。
- **无 GMS 设备**：v1 合格设备定位为「GMS + 端侧识别可用」；荣耀路径用 sherpa 绕开 Google 识别，但厂商识别接入仍是明确不做的范围。
- **总结覆盖窄**：见第 2 节；导出是所有人都能完成的闭环。

## 4. 设备限制与验证缺口

- **唯一验证过的真机**：荣耀 ALP-AN00（MagicOS 8.0 / Android 14，骁龙 8+ Gen 1 / 16 GB）；2026-09-07 真机自检。**所有质量与延迟数字只在该设备口径下成立。**
- **未验证设备**：Pixel 8/9、Android 14 三星、无端侧识别机（原真机清单 M5 未完成）；挖孔 / 平放倒字的触控与无障碍也只在上述荣耀机检查过。
- **未真机复验的改动**：2026-09 的延迟优化（ticker、流式回字幕、`ComputeGate`、投机 prefill、增量翻译）代码已落地，但 `_archive/2026-11/10-latency-optimization.md` 明确记录「待编译、待真机验证」；后续 harness 改造未动业务逻辑，**不改变该结论**。
- **JVM 单测边界**：65 个单测只覆盖纯逻辑（路由 / 组装 / 状态机 / 提示词等），不证明听写、翻译、TTS、Room 在真机上的行为；CI 无真机，禁止用模拟器绿条代替真机结论。
- **模型质量**：翻译质量结论来自开发期人工阅读，没有固定测试集与可复核证据；质量声明在补充夹具前一律按「未验证」处理。

## 5. 底线（不打折，违背算产品错误）

- 任务必须显式「新任务 → 结束任务」；只有 ended 进历史；空稿结束自动删除；暂停 ≠ 结束。
- 杀进程能恢复未结束任务；不存录音、不上传音频、不账号、无后端。
- 无耳机禁止翻译读出；总结对不支持设备不说「请打开」；分享走系统面板。
- 倒字用整块旋转，不镜像字形；竖屏锁定；离开前台即停听写（不做后台麦克风前台服务）。
- 未验证的能力不写成已验证；环境跑不通不写成代码通过。

## 维护

- 修缺陷：本页状态改 `已修` 并附提交短 hash / 证据 ID；新增缺陷追加 D-7 起编号，不要覆盖历史。
- 桩决策落地后：把「现状 / 产品呈现 / 建议」更新为最终结论，并在 [`03-decisions.md`](03-decisions.md) 对应 D 行改状态。
- 相关：决策 [`03-decisions.md`](03-decisions.md) · 路线图 [`06-roadmap.md`](06-roadmap.md) · 延迟 [`08-latency.md`](08-latency.md) · 现状速览 [`09-current-state.md`](09-current-state.md) · 文档索引 [`README.md`](README.md) · 历史档案 [`_archive/README.md`](_archive/README.md)。
