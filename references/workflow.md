# 任务分级、计划与红队

> 触发：方案设计、L2、跨会话、接手或独立审查前读。完成判据见 [`verification.md`](verification.md)。

## 1. L0 / L1 / L2

| 级别 | 例子 | 动作 |
| --- | --- | --- |
| L0 | 文档/注释、单文件小改、只读排查 | 直接做，跑最小检查 |
| L1 | 单模块行为修复、补测试 | 5–10 行短方案 + 验收 |
| L2 | 跨模块、规则/工具/CI、发布 | 完整方案 + 用户确认；并发/持久化/发布强制独立红队，其他 L2 自检 |

## 2. 计划纪律

- 计划放 `harness/plans/`，同一时间只有一个 active；front matter 必填 id/status/level/owner/updated/scope/acceptance/verify。
- 「未提交改动」必须与 `git status` 一致，否则 `tools/check_plan.py check` 红；done 必须填 submitted 并归档；越界先改 scope。
- 当前 active 计划见 [`../harness/plans/2026-11-10-android-adoption.md`](../harness/plans/2026-11-10-android-adoption.md)。

## 3. 证据纪律

- 先提交再取证（clean tree）；一条结论一个证据文件；verdict 只取 PASS/FAIL/UNVERIFIED；完成声明必须引用证据 ID，无证据即未验证。
- 测试声明附 JUnit 结果与命令；环境阻塞写「未验证 + 手动步骤」。

## 4. 停止条件

- 同一失败修 2 次仍不过，或同一子任务 3 轮无进展：停手，按阻塞报告上报并记入计划；环境/网络/已知不稳定不计修复次数。

## 5. 交接与恢复

- 中断前更新计划：进度、证据、未验证、未提交、下一步（一条具体动作）。
- 恢复：`make check` → `make verify-static` → `python3 tools/check_plan.py brief` → `make verify-claim`。

## 6. kit 升级

- 本仓镜像 harness-kit v0.2.2（kit 文件不手改、不分叉）。新版先 `--dry-run` 比对再合并，冲突以新版为准，本仓差异回写计划。

## 7. 红队最小协定

- 只读；输入 = 任务 + 方案 + 仓库路径（不传起草历史/自评）；输出结论 + P0/P1/P2 表 + 被挑战假设 + 缺失信息 + 最小验证清单；作者逐条回应，P0/P1 执行前解决。
