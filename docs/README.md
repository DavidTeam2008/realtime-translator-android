# 文档索引 · Android

> 状态：当前（2026-11-10）｜真源：代码、测试与证据；文档解释事实，冲突时以代码与最新验证为准。
> 本页是 `docs/` 的**唯一索引**：只维护「现行」文档一套；历史过程在 [`_archive/README.md`](_archive/README.md)（只读，不作为现状引用）。
> 新增/删除文档必须同步本页与 `harness/config.json` 的公开文档白名单，否则 `make check` 失败。

## 先读哪几篇

| 你的目的 | 阅读顺序 |
| --- | --- |
| 第一次来 / 想跑起来 | [`../README.md`](../README.md) → [`../CONTRIBUTING.md`](../CONTRIBUTING.md) → [`09-current-state.md`](09-current-state.md) |
| 接手 / 恢复任务 | [`../AGENTS.md`](../AGENTS.md) → `../harness/plans/`（active）或最近归档计划 [`../harness/plans/_archive/2026-11-10-android-adoption.md`](../harness/plans/_archive/2026-11-10-android-adoption.md) → [`09-current-state.md`](09-current-state.md) |
| 理解产品规则 | [`01-product.md`](01-product.md) |
| 理解架构 / 改分层 | [`02-architecture.md`](02-architecture.md) → [`../references/contracts.md`](../references/contracts.md) |
| 追问「为什么这样选」 | [`03-decisions.md`](03-decisions.md)（决策唯一表） |
| 改听写 / 翻译 / 字幕 / TTS | [`04-runtime.md`](04-runtime.md) → [`07-on-device-llm.md`](07-on-device-llm.md) |
| 看已知问题与取舍 | [`05-known-issues.md`](05-known-issues.md) |
| 看接下来做什么 | [`06-roadmap.md`](06-roadmap.md) + active 计划 |
| 查延迟数字与优化方案 | [`08-latency.md`](08-latency.md) |
| 写 / 改文档 | [`AGENTS.md`](AGENTS.md)（本目录规则） |
| 验证 / 提交前 | [`../references/verification.md`](../references/verification.md) |

## 当前文档

| 文档 | 内容 | 状态 / 维护要求 |
| --- | --- | --- |
| [`../README.md`](../README.md) | 项目入口：定位、快速开始、工具链约束、真机信息 | 产品定位/环境变化时同步 |
| [`AGENTS.md`](AGENTS.md) | 本目录规则：状态头、单一真源、归档与索引 | 文档规则变化时同步 |
| [`01-product.md`](01-product.md) | 产品规则：四模块行为、任务语义、设备分叉、诚实原则 | **产品行为唯一真源**；行为变化时更新 |
| [`02-architecture.md`](02-architecture.md) | 当前架构：分层/依赖、导航、任务、字幕模型、持久化、引擎边界、模型管理、错误模型 | 代码结构或依赖方向变化时同步 |
| [`03-decisions.md`](03-decisions.md) | 决策唯一表（D 编号）与仍成立的约束 | **决策唯一真源**；只追加，不改历史结论 |
| [`04-runtime.md`](04-runtime.md) | 运行时：音频→VAD→听写→切句→路由→翻译→字幕→TTS→落盘，含关键可调参数 | 引擎/参数变化时同步；数字口径见 07/08 |
| [`05-known-issues.md`](05-known-issues.md) | 已知问题、桩功能、未验证项与取舍 | 问题状态变化时更新；修复后移入「已解决」 |
| [`06-roadmap.md`](06-roadmap.md) | Now / Next / Later 方向 | 只写方向；进度以 active 计划与证据为准 |
| [`07-on-device-llm.md`](07-on-device-llm.md) | 端侧 LLM（TranslateGemma）原理、优化与真机数字 | 核心资产；数字必须标日期与设备 |
| [`08-latency.md`](08-latency.md) | 延迟归因、优化方案与实施状态 | 核心资产；数字必须标日期与设备 |
| [`09-current-state.md`](09-current-state.md) | 现状速览：可用能力/桩/与原设计偏差/验证状态 | 阶段变化时更新；细节不重复 05 |

## 历史档案

| 档案 | 说明 |
| --- | --- |
| [`_archive/README.md`](_archive/README.md) | 历史文档索引：2026-09 设计期文档（产品原型、架构、选型、实现原理、阻碍、妥协、路线图、端侧 LLM）与 2026-11 过程快照（现状、延迟）。**只读、保留当时口径、不改写正文、不作为现状引用。** |

> 归档规则：原文用 `git mv` 移入 `docs/_archive/<批次>/`，只加日期与状态头；当前文档重写为事实真源。`check_docs` 跳过 `_archive/`。

## 证据与计划

- 计划与进度唯一真源：`../harness/plans/` 的 active 计划；证据与三值判定见 `../harness/evidence/`。
- 审查报告放 `../harness/reviews/`；交接与命令见 [`../references/verification.md`](../references/verification.md)、[`../references/workflow.md`](../references/workflow.md)。
- 代码契约与边界见 [`../references/contracts.md`](../references/contracts.md)；根规则见 [`../AGENTS.md`](../AGENTS.md)。

## 维护约定

- **单一真源**：同一事实只在一篇维护，其余文档只引用；规则写根 `AGENTS.md` / `references/`，不进 docs。
- **状态头**：当前文档用 `> 状态：当前（YYYY-MM-DD）｜真源：…`；历史只在 `_archive/`，不改写。
- **新增/归档**：新增 `docs/*.md` 必须登记本页；归档必须更新 `_archive/README.md` 的对应关系。
- **链接与格式**：只用相对路径；代码引用写类型/函数名，不写易漂移行号；围栏成对；不写本机绝对路径、设备 ID、密钥。
- **验证**：文档改动跑 `make check`（链接/围栏/索引/白名单/预算）；失败修内容，不删检查绕过。
