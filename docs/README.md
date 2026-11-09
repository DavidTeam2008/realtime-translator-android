# 文档索引

> 本页是 `docs/` 的唯一索引：新增文档必须登记，否则 `make check` 失败。
> 事实以代码、测试与证据为准；文档与代码冲突时以代码为准并顺手修正文档。
> 最后更新：2026-11-10（接入 harness-kit 0.2.2；文档蒸馏在 P2 进行，届时 01–08 原文归档到 `docs/_archive/`）。

## 先读哪几篇

| 你的目的 | 阅读顺序 |
| --- | --- |
| 刚接手项目 | [`../AGENTS.md`](../AGENTS.md) → 本页 → [`AGENTS.md`](AGENTS.md) → [`../harness/README.md`](../harness/README.md) |
| 查规则与边界 | [`../references/contracts.md`](../references/contracts.md) |
| 查验证与命令 | [`../references/verification.md`](../references/verification.md) |
| 查分级 / 计划 / 红队 | [`../references/workflow.md`](../references/workflow.md) |

## 当前文档

| 文档 | 内容 | 状态 / 维护要求 |
| --- | --- | --- |
| [`AGENTS.md`](AGENTS.md) | 本目录增量规则：索引、单一真源、历史口径 | 规则变化时同步 |
| [`01-product-prototype.md`](01-product-prototype.md) | 产品原型与产品规则 | 产品规则变化时更新 |
| [`02-architecture.md`](02-architecture.md) | 架构设计（含早期引擎名，见 09 偏差表） | **待 P2 重写为当前架构** |
| [`03-tech-choices.md`](03-tech-choices.md) | 技术选型（写于实现之前） | **待 P2 蒸馏为决策表，原文归档** |
| [`04-implementation-principles.md`](04-implementation-principles.md) | 实现原理（写于实现之前） | **待 P2 重写/归档** |
| [`05-obstacles.md`](05-obstacles.md) | 实现阻碍点 | 待 P2 蒸馏当前约束 |
| [`06-compromises.md`](06-compromises.md) | 功能与效果妥协点 | 待 P2 蒸馏 |
| [`07-roadmap.md`](07-roadmap.md) | 落地路线图（早期甘特） | 待 P2 蒸馏为 Now/Next/Later |
| [`08-on-device-llm.md`](08-on-device-llm.md) | 端侧大模型技术资料 | 核心资产，P2 校数后保留 |
| [`09-current-state.md`](09-current-state.md) | 实现现状与已知缺陷 | 核心资产，持续更新 |
| [`10-latency-optimization.md`](10-latency-optimization.md) | 延迟归因与优化方案 | 核心资产，持续更新 |

## 历史档案

P2 文档蒸馏后，`01–08`（及 `09/10` 的过程快照）原文移入 `docs/_archive/`：只加日期与状态头，不改写正文；`check_docs` 跳过 `_archive/`，不作为现状引用。

## 证据与审查

- 计划与证据的存放约定见 [`../harness/AGENTS.md`](../harness/AGENTS.md)（证据目录由 standard profile 启用）。
- 审查报告放 `../harness/reviews/`；根因与过程记录见 active 计划。

## 维护约定

- 新增 `docs/*.md` 必须登记到本页，否则 `make check` 失败。
- 只写事实与理由；规则放根 `AGENTS.md` 与 `references/`，不在 docs 复制。
- 链接一律用相对路径；代码围栏必须成对闭合；不写本机绝对路径/设备 ID。
- 历史 / 案例类文档保留当时口径；结论变化时新增带日期段落，不改写历史数字。
