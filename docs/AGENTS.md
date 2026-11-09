# docs/AGENTS.md · 文档目录规则

> 状态：当前（2026-11-10）｜真源：本页是 `docs/` 的增量规则；索引见 [`README.md`](README.md)，项目规则见 [`../AGENTS.md`](../AGENTS.md)。
> 触发：新增、重写、移动或归档 `docs/*.md` 前读本页。

## 1. 状态头（每篇必须有）

- **当前文档**：文件开头写一行
  `> 状态：当前（YYYY-MM-DD）｜真源：<代码路径 / 计划 / 证据>`
- **历史文档**：只放在 `_archive/`，开头写
  `> 状态：历史（YYYY-MM-DD）｜快照，不作为现状引用`
  正文保留当时口径，**不改写数字与结论**；需要更新时新增带日期的订正段。
- 过期结论在原文开头加「YYYY-MM-DD 订正」，不删除历史证据。

## 2. 单一真源（写哪一篇）

| 事实 | 唯一位置 |
| --- | --- |
| 文档索引与路由 | [`README.md`](README.md)（只此一处） |
| 产品行为 / 任务语义 | [`01-product.md`](01-product.md) |
| 架构、分层与依赖 | [`02-architecture.md`](02-architecture.md) |
| 决策与理由（D 编号） | [`03-decisions.md`](03-decisions.md)；其他文档只引用 D 编号 |
| 运行时流水线与参数 | [`04-runtime.md`](04-runtime.md) |
| 已知问题 / 桩 / 未验证项 | [`05-known-issues.md`](05-known-issues.md)；09 只做速览，不重复细节 |
| 方向（Now/Next/Later） | [`06-roadmap.md`](06-roadmap.md)；进度以 active 计划 + 证据为准 |
| 端侧 LLM 原理与数字 | [`07-on-device-llm.md`](07-on-device-llm.md) |
| 延迟归因与方案 | [`08-latency.md`](08-latency.md) |
| 现状速览 | [`09-current-state.md`](09-current-state.md) |
| 规则 / 命令 / 验证矩阵 | 根 `AGENTS.md`、`references/`（**不写进 docs**） |

- 同一事实只在一篇维护；其他文档写「见 X」并给相对链接。
- 数字（延迟、模型大小、测试计数）必须带日期、设备或口径；只引用一个来源。

## 3. 新增、归档与索引

- 新增 `docs/*.md`：必须登记到 [`README.md`](README.md) 的「当前文档」表，并同步 `harness/config.json` 的公开文档白名单（如启用）。否则 `make check` 失败。
- 命名：小写短横线、一个主题一篇；当前规范用 `NN-topic.md`，专题（决策/现状速览）可用语义名。
- 归档：用 `git mv` 移到 `docs/_archive/<批次>/`，更新 [`_archive/README.md`](_archive/README.md) 的「归档 → 当前对应」关系，并把所有引用改到当前文档。
- `_archive/` 只读、不参与 `check_docs` 扫描，也不作为现状引用。

## 4. 链接与格式

- 只用相对链接（CI 区分大小写）；链接目标必须是最终会存在的路径。
- 引用代码写类型 / 函数名，不写易漂移行号；关键以代码为准。
- 不写本机绝对路径（home 目录、挂载盘）、设备 ID、序列号、密钥/Token。
- 代码围栏成对闭合；表格不要塞入过长命令，长命令放代码块。
- 删除旧文档前先确认没有其他文档引用；引用先改，再删。

## 5. 验证

- 文档改动跑 `make check`（链接 / 围栏 / 索引 / 白名单 / 预算）；失败先修链接与索引，不靠删内容变绿。
- 声称「已验证 / 数值如此」必须有来源（代码、测试、证据、计划）；无法验证时写「未验证 + 原因」。
