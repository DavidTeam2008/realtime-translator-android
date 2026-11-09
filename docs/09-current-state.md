# 09 现状速览 · 对译 Duiyi Android

> 状态：当前（2026-11-10）｜真源：代码与测试；细节问题与取舍见 [`05-known-issues.md`](05-known-issues.md)，决策见 [`03-decisions.md`](03-decisions.md)，方向见 [`06-roadmap.md`](06-roadmap.md)。

**一句话**：纯端侧的多语言现场沟通 App——荣耀真机主路径已跑通（SenseVoice 听写 → 语种路由 → TranslateGemma 4B 翻译 → 字幕/朗读），**翻译质量可接受，但端到端延迟偏大**（数字见 08）；总结等多处仍是桩，明确标注、不假装可用。

## 1. 当前可用能力

| 模块 / 能力 | 状态 | 说明 |
| --- | --- | --- |
| 引导 Onboarding | ✅ 可用 | 语言选择 → 麦克风权限 → 下载模型；文案按设备分叉（荣耀含 SenseVoice） |
| 首页 Home | ✅ 可用 | 三模块卡 + 历史入口 + 未结束任务；设置（语言/字号/能力说明/模型入口） |
| 面对面 Conversation | ✅ 真机主路径 | 上下分屏、上屏 180°、双向翻译、语种路由、串扰抑制；默认自动开听 |
| 同声传译 Interpretation | ✅ 可用 | 单栏单向；不自动开听；TTS 需耳机、队列 2、增量后缀朗读 |
| 会议记录 Meeting | ✅ 可用 | 单语全文稿、不翻译、进入即卸载 4B、2 万字符提示续集 |
| 任务历史 History | ✅ 可用 | Room 列表、左滑删除、详情只读、UTF-8 txt 系统分享 |
| 模型和资源包 Models | ⚠️ 半成品 | 展示进度/占用、可下载/删除；按语言对管理未实现（见 05） |
| 端侧翻译 | ✅ 可用 | TranslateGemma 4B Q4_K_M，全部六语共用一份权重 |
| 端侧听写 | ✅ 荣耀可用 | 荣耀/华为 → SenseVoice int8 + Silero VAD；其他厂商走系统识别器（未真机验证） |

## 2. 未完成 / 桩（实现现状以代码为准）

| 项 | 现状 | 用户可见行为 |
| --- | --- | --- |
| 会后总结 | `HonestSummarizer` 桩：恒 `DeviceNotEligible` | 点「总结」明确提示「这台手机不能在本机生成摘要」，可导出（不假装可用） |
| 音频会话策略 | `AudioSessionPolicy` 三档 use case 同构（均 `MODE_NORMAL`） | 耳机检测可用；面对面 AEC / 同传读出的分场景参数未实现（不宣称） |
| 设备语言能力探测 | `DeviceCapabilityProbe` 的 installed/supported locales 为空集，目录退化为中英可用 | 部分语言被保守判为不可用；泰/越全链路不可用 |
| 按语言对下载 | 一个 4B GGUF 覆盖全部语言对；`downloadLanguage/deleteLanguage` 写死 English | 没有「按语言对按需下包」，模型页只展示整包 |
| 部分结果翻译 | 已删除（只译 final）；`TranslationPolicy` 的节流常量成为死代码 | 长句要等说完才出译文（结构性问题，见 08） |

> 以上不是「待办清单复制」：细节、根因与取舍见 05；决策依据见 03。

## 3. 与原设计的偏差（短表）

| 项 | 设计期（已归档） | 当前实现 | 相关决策/问题 |
| --- | --- | --- | --- |
| 翻译引擎 | ML Kit Translation + 六语语言包 | llama.cpp + TranslateGemma 4B Q4_K_M（全 CPU） | 03（D 系列）/ 07 |
| 听写引擎 | 系统端侧 `SpeechRecognizer` + 语言检测 | 荣耀/华为 → SenseVoice + Silero VAD；其他厂商 → 系统识别器 | 03 / 05 |
| 翻译时机 | 部分结果节流送译 | 默认只译 final；增量翻译为可选开关 | 08 / 05 |
| 会后总结 | Gemini Nano 三态 | 桩：恒「本机不可用」 | 03 / 05 |
| 语言能力目录 | `checkRecognitionSupport` 动态能力 | 探测降级为「中/英可用」 | 05 |
| 模型下载 | 按语言对下载 | 单份 4B 权重 + 整包管理 | 05 |

> 设计期原文已归档到 [`_archive/README.md`](_archive/README.md)，仅作历史口径，不作为现状引用。

## 4. 验证状态

| 项 | 状态 | 说明 |
| --- | --- | --- |
| JVM 单元测试 | ✅ 65 个，0 失败 0 跳过（P3 清洁后复跑 PASS，2026-11-10） | `./scripts/verify-unit.sh`；基线写入 `harness/test-baseline.json`（unit.floor=65），改动后须保持只增不减 |
| 真机手工验证 | ⚠️ 仅荣耀 ALP-AN00（型号） | 面对面主路径、同传、会议、历史、导出在开发真机手测过；非荣耀机型未验证 |
| 延迟数字 | 📎 见 08 | 端到端/首字/生成等数字与日期在 [`08-latency.md`](08-latency.md) |
| 端侧 LLM 数字 | 📎 见 07 | 加载、前缀预热、生成数字与设备口径在 [`07-on-device-llm.md`](07-on-device-llm.md) |
| 证据链 | 🚧 进行中 | `make verify-static` 已接；`tests-pass` 证据与 JUnit 适配在 harness 改造计划 P4（见下一节） |
| 非荣耀真机 / 泰越 / 总结 / 音频策略 | ❌ 未验证 | 只做了代码与 JVM 测试；不得写成已通过 |

> 验证规则（完成声明、证据三值、未验证写法）见 [`../references/verification.md`](../references/verification.md)。

## 5. 下一步

- 方向与优先级见 [`06-roadmap.md`](06-roadmap.md)：延迟（最高）→ 诚实度（桩功能实现或从 UI 撤掉）→ 工程卫生。
- 执行中的任务与验收以 active 计划与证据为准：[`../harness/plans/2026-11-10-android-adoption.md`](../harness/plans/2026-11-10-android-adoption.md)。
- 现状变化时更新本页与 05；数字（延迟/模型/测试计数）更新时必须带日期与设备口径。
