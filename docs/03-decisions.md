# 03 决策表 · Android

> 状态：当前规范（**唯一决策表**）。最后核对：2026-11-10（对照当前工作树代码）。
> 原始选型推演在 `_archive/2026-09-design/03-tech-choices.md`（历史记录，只保留当时口径，不改写）。
> 状态口径：`生效` = 当前代码按此实现；`被替代` = 旧选择已废弃；`未实现` = 决策已定但代码是桩/空实现；`待定` = 尚未决策。
> **「生效」只代表代码按此实现，不代表已通过真机验收**；设备与验证范围见 [`05-known-issues.md`](05-known-issues.md)，进度与后续安排见 [`06-roadmap.md`](06-roadmap.md)。
> 文档与代码冲突时以代码为准，并顺手修正本表；决策变化只改「当前选择 / 状态」，被替代的选择保留而不是删除。

## 决策总表

| ID | 问题 | 当前选择 | 放弃项 | 理由 | 状态 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| D1 | 端侧优先，是否允许静默云降级 | 听写与翻译只走端侧；任何云路径都不做运行时降级 | 云 STT / 云翻译、默认 `createSpeechRecognizer()` 的联网路径 | 产品承诺「音频不出设备」；静默上云不可接受 | 生效 | `SpeechEnginePolicy.useGoogleSpeechIntent()` 恒 false；翻译只有 `GemmaTranslator` |
| D2 | 听写引擎 | 荣耀 / 华为 → sherpa-onnx SenseVoice int8 + Silero VAD；其他厂商 → 系统 `SpeechRecognizer`（端侧优先） | 单一系统识别器、云 STT、两个识别器并行 | 荣耀机系统引擎对第三方无回调、拿不到可控端点；自持音频才能做 VAD | 生效（非荣耀路径未真机验证） | `SpeechEnginePolicy`、`SherpaSpeech`、`AndroidSpeechEngine` |
| D3 | 翻译引擎 | llama.cpp + TranslateGemma 4B Q4_K_M（GGUF，约 2.49 GB），全 CPU，前缀 KV 快照 | ML Kit Translation、云翻译、专用 NMT（尚未评估完） | 六语都有、无 GMS 依赖；ML Kit 在无 GMS 的荣耀真机不可用 | 生效 | `GemmaModelSpec`、`GemmaTranslator`、`LlamaNative`、`TranslationPump` |
| D4 | 语种路由 | SenseVoice 自带 `lang` 标签 + 文本脚本推断融合；系统语言检测只在非荣耀路径作辅助票 | 系统 `onLanguageDetection` 当主票、独立 LID 模型、双识别器 | 荣耀路径没有系统语言回调；单识别器限制下只能靠文本证据 | 生效 | `SenseVoiceText.languageFrom()`、`SpeechTextRouter`、`UtteranceAssembler` |
| D5 | 切句（端点与短句） | Silero VAD 端点（`minSilenceDuration=0.55s`、`maxSpeechDuration=20s`）+ `SpokenSegmentJoiner` 缓冲（`HOLD_NS=1.4s`） | 系统静音窗 extras、只等 `onResults` 终稿 | 荣耀机不可依赖 OEM extras；端点延迟与短句可用性需自己控 | 生效 | `SherpaSpeech.createVad()`、`SpokenSegmentJoiner` |
| D6 | 翻译时机 | 默认只译 `isFinal`；partial 只用于投机 prefill（省源句 prefill）；增量分段翻译是实验开关，默认关 | 部分结果实时重译（已证伪：译文跳变 + 队列拥堵） | 字幕单调稳定优先；重译会挤占唯一翻译通道 | 生效（缺陷 D-2：长句要等说完） | `ConversationViewModel.enqueueTranslation()`、`InterpretationViewModel.enqueueTranslation()`、`PreferencesStore.incrementalTranslation` |
| D7 | 音频会话（场景区分） | 统一 `MODE_NORMAL` + 耳机路由门禁（无耳机禁止读出）；「面对面关 AEC / 同传读出开 AEC」未做 | 分场景 `UNPROCESSED` / `VOICE_COMMUNICATION` 完整区分 | 系统识别器不提供 PCM 注入，`AudioSource` 常被 OEM 忽略 | 未实现（三分支同构） | `AudioSessionPolicy.activate()`、`InterpretationViewModel` 耳机门禁 |
| D8 | 语言能力目录 | `DeviceCapabilityProbe` 目前返回空 `installedSpeechLocales` / `supportedSpeechLocales`；目录按 provider 退化（见备注） | `checkRecognitionSupport` 动态目录、真实语种探测 | OEM 探测 API 不稳定，先保证主路径可用 | 未实现（探测空集） | `DeviceCapabilityProbe.probeNow()`、`DeviceLanguageCatalog` |
| D9 | 会后总结 | 不上云；`HonestSummarizer` 桩：`availability()` 恒 `DeviceNotEligible`，`summarize()` 抛错；四个模块仍有「总结」入口 | Gemini Nano / AICore 实现、云摘要 API | AICore 覆盖极窄；对不支持设备保持诚实三态 | 未实现（桩） | `HonestSummarizer`、`SummarySheet` |
| D10 | 存储与落盘 | Room 持久化 + `InMemoryTaskStore`（测试/替身）；内存态为准，约 250 ms 异步全量落盘 | DataStore / 整场塞一个 TEXT / 手写 SQLite | 列表、恢复、删除、测试替身都更简单 | 生效 | `RoomStore`、`TaskSessionController.persist()`、`TranslationPolicy.PERSIST_MS` |
| D11 | UI / 状态 / DI | Jetpack Compose + Material 3 + 自有 Tokens；ViewModel + StateFlow；Hilt | XML/ViewBinding 主界面、Orbit/MVI 套件、Koin | 倒字板/分屏/状态驱动字幕是声明式强项；生命周期与官方路径一致 | 生效 | `app/build.gradle.kts`（compose / hilt）、`designsystem/`、各 `*ViewModel` |
| D12 | 最低系统与 ABI | `minSdk 34`、`targetSdk 35`；仅 `arm64-v8a` | API 26 兼容、32 位 / x86 模拟器支持 | 端侧多语种与语言切换 API 的门槛；llama.cpp 只构建 arm64 | 生效 | `app/build.gradle.kts` 的 `minSdk` / `ndk.abiFilters` |
| D13 | 导出 | `cacheDir/exports` 生成 UTF-8 `.txt`，`FileProvider` + `ACTION_SEND` 走系统分享面板 | 微信 SDK、云导出、深链分享 | 审核成本低、隐私边界清楚、无第三方依赖 | 生效 | `TranscriptExportService`、`Sheets.kt` |
| D14 | 模型管理 | 一个 Gemma 4B GGUF 覆盖全部语言对 + SenseVoice 权重按需下载（引导页进度）；「按语言对下载/删除」未实现，`DeviceAssetCatalog` 仍留有写死 `English` 的方法 | 按语言对打包与下载、按需换模型 | 单 4B 已覆盖六语，实现简单；代价是首次体积大 | 部分未实现 | `GemmaModelStore`、`SherpaModelStore`、`DeviceAssetCatalog.downloadLanguage()` |
| D15 | 隐私与数据 | 无后端、无账号、不存录音、音频不上传；模型下载是唯一网络用途 | 云同步 / 账号体系 / 分析 SDK | 隐私定位与商店数据安全表一致 | 生效 | `AndroidManifest.xml`（仅 INTERNET 用于下载）；`RemoteFileDownloader` |

## 逐条备注（实现细节与状态偏差）

- **D2 非荣耀路径**：代码保留 `SpeechRecognizer`（含 `EXTRA_PREFER_OFFLINE`、语言检测/切换 extras 与自动续听），但只在荣耀机做过真机验证；Pixel / 三星等厂商路径没有设备级验证记录，**产品不得按同等质量承诺**。
- **D4 融合顺序**：脚本证据足够强时（`SpokenText.scriptIsDecisive`）直接采用脚本语种；否则才参考系统检测，最后回退 `lastLanguage`。没有系统回调的荣耀路径完全依赖 SenseVoice 标签 + 脚本。
- **D5 端点口径**：0.55 s 是「说完到切段」的固定代价，`HOLD_NS=1.4 s` 是短句攒句上限；两者都计入端到端延迟预算（见 [`08-latency.md`](08-latency.md)）。
- **D6 现状**：`enqueueTranslation()` 默认路径下 `if (!isFinal) return` 之前只做投机 prefill；只有打开「增量翻译」设置才会按稳定前缀分段送译。默认行为因此仍是「长句等说完」，即缺陷 D-2。
- **D7 已实现的部分**：耳机路由监听（`AudioDeviceCallback`）与「无耳机禁止读出」是生效的；未实现的是**场景化的音频模式/AEC 区分**，三个 `AudioUseCase` 分支当前代码完全同构。
- **D8 退化规则**：`DeviceLanguageCatalog` 在荣耀 sherpa 路径下固定放行中 / 英 / 日 / 韩（SenseVoice 模型覆盖的语言），其余情况回退「中 / 英」；翻译方向因单 4B 全语对而普遍放行。泰语 / 越南语在荣耀路径**听写不可用**（翻译仍可出），UI 需按能力灰置而不是承诺六语全绿。
- **D10 已知代价**：每 250 ms 落盘一次，但当前实现是「删掉该任务全部字幕再全量插回」（见 [`05-known-issues.md`](05-known-issues.md) D-4），长会议是 O(n²) 写放大。
- **D14 残留**：`DeviceAssetCatalog` 的 `downloadLanguage` / `deleteLanguage` 写死 `English`，与实际「单模型」行为不一致；Models 页面只有一张翻译模型卡。按语言对管理要么补实现，要么删接口（建议见 05 的桩清单）。

## 约束与风险

- **无后端 / 无上传 / 无账号**：网络只用于下载模型；「完全离线可用」只在模型就绪后成立，引导页必须如实要下载。
- **真机验证范围**：仅荣耀 ALP-AN00（MagicOS 8.0 / Android 14，骁龙 8+ Gen 1 / 16 GB）有真机记录（2026-09 自检）；Pixel / 三星 / 无端侧识别机未验证（详见 [`05-known-issues.md`](05-known-issues.md)）。
- **首次成本**：翻译模型约 2.49 GB（`GemmaModelSpec.EXPECTED_BYTES`），听写权重约 240 MB；真机自检 `prepare` 约 18 s，首次点「听」的等待反馈很弱。
- **延迟**：面对面端到端约 2–2.7 s（荣耀真机口径），是当前最大体验问题；结构性原因在三层串行（VAD → 整段 ASR → 整句 LLM），见 [`08-latency.md`](08-latency.md)。
- **平台折扣**：Android 没有 iOS 的双路 `SpeechAnalyzer`，单识别器下「两人同时说 / 快速换语言」只能尽力而为；远场听写、TTS 引擎质量、蓝牙 SCO 与读出的取舍见 [`05-known-issues.md`](05-known-issues.md)。
- **无 GMS 设备**：v1 合格设备定位为「GMS + 端侧识别可用」；荣耀路径用 sherpa 绕开 Google 识别，但国内无 GMS 机型的厂商识别接入仍是明确不做的范围。

## 维护

- 新增决策追加 D16 起编号；变更时改「当前选择 / 状态」，把旧选择标 `被替代` 并保留。
- 依据优先写**类型名 / 函数名 / 常量名**，少写行号（易漂移）；原始推演留在归档，不在本表复制历史。
- 相关：已知问题 [`05-known-issues.md`](05-known-issues.md) · 路线图 [`06-roadmap.md`](06-roadmap.md) · 现状速览 [`09-current-state.md`](09-current-state.md) · 文档索引 [`README.md`](README.md) · 历史档案 [`_archive/README.md`](_archive/README.md)。
