# HARNESS · 对译 Duiyi Android

> 本仓 harness 地图（不是 kit 说明书）：**guides（指令）+ sensors（门禁/证据）**怎么落地、怎么用、边界在哪。
> 规则入口 [`AGENTS.md`](AGENTS.md)；文档索引 [`docs/README.md`](docs/README.md)；当前进度见 active 计划。

## 1. 目标

让“做完了”可复跑、可否定、可交接：规则有入口、状态有唯一真源、证据有判定、范围可拦截。
失败声明应被机器拦住，而不是靠人记得。

## 2. 五子系统落点

| 子系统 | 作用 | 本仓资产 / 入口 |
| --- | --- | --- |
| Instructions | 该做什么、去哪读 | [`AGENTS.md`](AGENTS.md) + `docs/AGENTS.md` + `harness/AGENTS.md` + [`references/`](references/verification.md)；`make check` 校验预算/引用/链接 |
| State | 做到哪、上次结论 | `harness/plans/`（唯一 active 计划）+ `harness/evidence/`（证据摘要）+ `harness/test-baseline.json` |
| Verification | 怎么证明做完了 | `make check` / `make verify-static` / `make verify-claim`；单测 `./scripts/verify-unit.sh`；真机手工验收 |
| Scope | 允许改什么 | 计划 front matter 的 `scope.allow/deny` + L0/L1/L2 分级（`make check` 内的 check_plan 拦越界） |
| Session Lifecycle | 怎么接手、怎么收尾 | `harness/README.md` 接手步骤 + 计划状态机 + pre-push / CI（静态） |

## 3. 计划工作流（跨会话唯一状态源）

1. 新建：`make plan TOPIC=<topic>` → 生成 `harness/plans/<日期>-<topic>.md`。
2. 填 front matter：`id/status/level/owner/updated/scope.allow/acceptance/verify`；**同一时间只允许一个 active**。
3. 改代码前写「目标与非目标 / 验收 / 改动范围」；越界先停，更新 `scope` 再继续。
4. 每步把「命令 | 结果 | 环境 | 证据ID」写进「验证证据」表；未跑/未验证单列。
5. 收尾：`make check` → `make verify-static`；完成改 `status: done` 并归档，交接写“下一步 1 条”。

## 4. 证据工作流（已启用，P4）

- 来源：`./scripts/verify-unit.sh` 产出的 JUnit XML；`make evidence-test` 一键跑测并取证。
- 静态门禁证据：`static-gates` claim（kit v0.2.3 起）用 `make verify-static` 取证；静态类 claim 由 `verify-claim` **复跑命令**判定，不能只写 verdict。
- 转换：`tools/evidence_from_junit.py` → `tools/evidence.py write`（自动填 UTC id / git commit / dirty；要求 clean tree）。
- 判定：`make verify-claim` 固定输出 `CLAIM <id>: PASS|FAIL|UNVERIFIED`，聚合退出码 FAIL→1 / UNVERIFIED→2 / 全 PASS→0。
- 规则：无证据 = 未验证；环境不可复核 = UNVERIFIED；原始产物（日志/构建目录）不入库，只存 1–3 KB 摘要。
- 当前状态：P4 已启用 `tests-pass`；2026-11-10 升级 kit v0.2.3 时补 `static-gates`，工具/门禁改动的完成声明引用它。

## 5. kit 版本与升级

- 采用版本：**harness-kit 0.2.3（standard profile）**；镜像源与 kit 源保持同版本，不 fork 本地脚本。
- kit 获取（独立仓 pinned，不 vendor）：
  ```bash
  git clone --depth 1 --branch v0.2.3 https://github.com/DavidTeam2008/harness-kit.git /tmp/harness-kit
  python3 /tmp/harness-kit/scripts/harness-adopt --target . --report /tmp/adoption.md   # 只读盘点
  python3 /tmp/harness-kit/scripts/harness-init --profile standard --target . \
    --name "对译 Duiyi Android" --language android --test-command "./scripts/verify-unit.sh" --dry-run
  ```
  离线备选：从来源仓 `realtime-translator-ios` 的 `harness-kit/` 目录同源拷贝（该仓为 kit 上游维护源）。
- 升级方式（2026-11-10 已实测 v0.2.2→v0.2.3）：kit 没有 in-place 升级命令，对已接入仓跑 `harness-init` 只会全 CONFLICT（还会想写 `Makefile.harness`）。实际做法：临时目录渲染新版 → 逐文件 diff → 只回写 kit 管理的 `tools/`、`harness/config.json`（kitVersion/配置）、Makefile 的 kit 目标段与 CI/hook；项目自有文档（AGENTS/CONTRIBUTING/README/docs/references）不回写 kit。
- 升级后必须重跑 `make verify-static`，并用 kit 侧 `python3 /tmp/harness-kit/scripts/harness-selftest --target .` 做负向注入复核；`harness/config.json` 是路径/命令/预算/claims 的唯一配置源。
- 宿主差异只剩配置与 Makefile 宿主目标（`check-quality`/`test`/`evidence-test`）；`tools/` 下 9 个脚本与 kit v0.2.3 逐字节一致（`check_plan` 无扩展名根文件声明、`check_hygiene`/`check_layers` 通用传感器均随上游）。

## 6. 当前门禁边界（不要过度声称）

| 层 | 覆盖 | 局限 |
| --- | --- | --- |
| 静态（CI + 本地） | 文档链接/索引/围栏/预算、指令预算与敏感串、计划状态与证据 schema | 只证明结构，不证明行为正确 |
| 单测（本地） | JVM 单测 65，floor 门禁 | 需要 JDK 17–21；不覆盖真机/引擎 |
| 真机（手工） | 听写/翻译/延迟/权限 | 无自动化，环境不可用即“未验证” |
| 宿主静态（CI + 本地） | `make check-host`：`check_hygiene`（卫生）+ `check_layers`（分层），kit v0.2.3 通用传感器，config 缺段时 `[SKIP]`；已并入 `verify-static` | 只做静态规则，不证明行为正确；负向注入由 kit `harness-selftest` 复核（8 项变异） |
| 宿主质量（本地） | `make check-quality`：detekt + ktlint + Android Lint（baseline 起步） | 需要 JDK 17–21/SDK；不跑 CI；存量债在 baseline |

- CI（`.github/workflows/verify.yml`）只跑 `make verify-static`，不跑单测/真机。
- 证据可伪造；三值判定提高说谎成本，不提供密码学保证。

## 7. 月度审计（简）

1. `make check`、`make verify-static`、`make verify-claim` 退出码与输出摘要。
2. 五个子系统各打分 1–5，附证据（文件/命令/证据 ID）；无证据项降级。
3. 检查：根 AGENTS 预算余量、active 计划是否唯一、未验证项是否清零、失败模式是否回写规则/门禁。
4. 结论写 `harness/reviews/`，重复 ≥2 次的失败转成新门禁或规则。
