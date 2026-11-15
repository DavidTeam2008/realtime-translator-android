# 文档索引 · Android

> 状态：当前（2026-11-16）｜真源：代码、测试与证据；文档解释事实，冲突以代码与最新验证为准。
> 本页是 `docs/` 的唯一索引；历史过程在 [`_archive/README.md`](_archive/README.md)（只读，不作为现状引用）。
> 新增/删除文档必须同步本页与 `harness/config.json` 的公开文档白名单，否则 `make check` 失败。

## 先读哪几篇

| 目的 | 阅读顺序 |
| --- | --- |
| 第一次来 / 跑起来 | [`../README.md`](../README.md) → [`../CONTRIBUTING.md`](../CONTRIBUTING.md) → [`09-current-state.md`](09-current-state.md) |
| 接手 / 恢复任务 | [`../AGENTS.md`](../AGENTS.md) → active 计划（`../harness/plans/`）→ [`09-current-state.md`](09-current-state.md) |
| 产品 / 架构 / 决策 | [`01-product.md`](01-product.md) → [`02-architecture.md`](02-architecture.md) → [`03-decisions.md`](03-decisions.md) |
| 运行时 / 端侧 LLM / 延迟 | [`04-runtime.md`](04-runtime.md) → [`07-on-device-llm.md`](07-on-device-llm.md) → [`08-latency.md`](08-latency.md) |
| 已知问题 / 方向 | [`05-known-issues.md`](05-known-issues.md) + [`06-roadmap.md`](06-roadmap.md) |
| 改文档 / 提交前 | [`AGENTS.md`](AGENTS.md) → [`../references/verification.md`](../references/verification.md) |

## 当前文档

- 产品与架构：[产品规则](01-product.md) · [架构/分层](02-architecture.md) · [决策表 D 编号](03-decisions.md)
- 运行时与模型：[运行时流水线](04-runtime.md) · [端侧 LLM](07-on-device-llm.md) · [延迟归因](08-latency.md)
- 状态与计划：[已知问题](05-known-issues.md) · [方向](06-roadmap.md) · [现状速览](09-current-state.md)
- 规则与索引：[文档目录规则](AGENTS.md) · [评分卡](harness-scorecard.md)（`make scorecard` 生成草稿，自评/独立复评分列）

## 历史档案

历史文档在 [`_archive/`](_archive/)，只读、保留当时口径、不作为现状引用；`check_docs` 跳过该目录。

## 证据与计划

- 计划与进度唯一真源：`../harness/plans/` 的 active 计划；证据与三值判定见 [`../harness/evidence/README.md`](../harness/evidence/README.md)。
- 验证矩阵见 [`../references/verification.md`](../references/verification.md)，契约见 [`../references/contracts.md`](../references/contracts.md)，审查报告放 `../harness/reviews/`。

## 维护约定

- 单一真源：同一事实只在一篇维护，其余引用；规则写根 `AGENTS.md` / `references/`，不进 docs。
- 状态头：当前文档用 `> 状态：当前（YYYY-MM-DD）｜真源：…`；历史只在 `_archive/`，不改写历史数字。
- 新增/归档：新增 `docs/*.md` 必须登记本页并同步白名单；归档用 `git mv` 到 `_archive/` 并更新索引。
- 链接与格式：只用相对路径；围栏成对；不写本机绝对路径、设备 ID、密钥；数字必须带日期/设备/口径。
