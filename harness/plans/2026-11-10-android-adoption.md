---
id: 2026-11-10-android-adoption
status: active
level: L2
owner: david
updated: 2026-11-10
scope:
  allow:
    - AGENTS.md
    - HARNESS.md
    - CONTRIBUTING.md
    - README.md
    - docs/
    - references/
    - harness/
    - config/
    - tools/
    - scripts/
    - Makefile
    - .gitignore
    - .github/
    - .githooks/
    - app/
    - gradle/
    - build.gradle.kts
    - settings.gradle.kts
    - gradle.properties
    - prototype/
    - third_party/
  deny:
    - app/build/
    - app/.cxx/
    - local.properties
    - .gradle/
    - .idea/
acceptance:
  - P1：`make check` 与 `make verify-static` exit 0；scaffold 已提交；65 个 JVM 单测保持全绿
  - P2：`docs/README.md` 覆盖 100% 文档；当前/历史两层分离；01–08 原文归档 `docs/_archive/`；`docs/03-decisions.md` 唯一决策表；`make check` exit 0
  - P3：绝对符号链接/被跟踪构建产物/本机路径/死代码/调试入口清理完成；跟踪文件中 `/local/`、`/local/` 0 命中；单测 65 全绿
  - P4：JUnit XML → `evidence.py` → `verify_claim` 端到端 PASS（`tests-pass`）；detekt/ktlint/Android Lint + 分层守卫接入 `make check-host`；pre-push/CI 跑静态门禁
  - P5：负向注入矩阵全部被拦截后恢复全绿；冷启动首访 5 问 ≥4 可答；计划 done/归档演练通过
verify:
  - make check
  - make verify-static
  - make verify-claim
---

# 2026-11-10-android-adoption · Android 仓 harness 改造（Stage B）

> 计划是跨会话任务的进度真源：中断 / 交接前更新，完成后归档。
> 根指令见 [`../../AGENTS.md`](../../AGENTS.md)，流程见 [`../../references/workflow.md`](../../references/workflow.md)，证据格式见 [`../evidence/README.md`](../evidence/README.md)。
> 评估依据：[`../reviews/2026-11-10-harness-adoption-assessment.md`](../reviews/2026-11-10-harness-adoption-assessment.md)；kit 版本 0.2.2（镜像仓 `v0.2.2`）。

## 目标与非目标

- 目标：按已确认的评估方案，把本仓从「文档/进度靠人维护」改造成「门禁 + 计划 + 证据可机械校验」；一次接入 standard profile，完成文档蒸馏、清洁、宿主传感器与验收。
- 非目标：不补产品功能（桩代码只做"实现/撤 UI/标未验证"决策）；不重写业务逻辑；不引入第三方 harness 依赖（kit 产物可删）；不把 Android 专用规则写进 kit 上游。

## 验收

- [ ] P1：`make check` / `make verify-static` exit 0；scaffold 提交；65 单测全绿
- [ ] P2：文档蒸馏完成（当前 docs 重写 + `_archive` 归档 + 索引 100%）；`make check` exit 0
- [ ] P3：清洁批次完成（符号链接/本机路径/死代码/调试入口）；跟踪文件 0 命中 `/local/`、`/local/`；65 单测全绿
- [ ] P4：`tests-pass` 证据经 `verify_claim` PASS；`make check-host`（detekt/ktlint/lint/分层）接入；pre-push/CI 生效
- [ ] P5：负向注入全红→全绿；冷启动首访 ≥4/5；计划归档演练

## 改动范围

- 允许：见 front matter `scope.allow`（README/docs/references/harness/tools/scripts/Makefile/CI/hooks/app 代码清理）
- 禁止：构建产物（`app/build/`、`app/.cxx/`）、本机配置（`local.properties`、`.gradle/`、`.idea/`）入库

## 进度

- [x] P1 接入 scaffold（2026-11-10）：kit 0.2.2 init standard `--language android`；修复 10 篇文档索引、跨仓断链、评估稿归档、config/baseline（unit floor=65）；`make check` / `make verify-static` PASS；scaffold 提交 `5179fdd`
- [x] P2 文档蒸馏（2026-11-10）：当前 docs 重写（01/02/04/09 + README/AGENTS）；01–08/09/10 原文归档 `docs/_archive/`；新增 `docs/03-decisions.md`（D1–D15 唯一决策表）、`docs/05-known-issues.md`、`docs/06-roadmap.md`、`docs/07-on-device-llm.md`、`docs/08-latency.md`；根 `AGENTS.md`/`CONTRIBUTING.md`/`HARNESS.md`/`README.md` 与 `references/` 三篇重写；`make check` PASS（164 条链接/11 篇公开文档/预算内）
- [x] P3 清洁批次（2026-11-10）：死代码/调试入口/llama.cpp 链接/本机脚本/`.gitignore` 全部处理；`check_layers` + `check_hygiene` PASS；65 单测复跑 PASS；debug/release manifest 合并已核
- [x] P4 传感器与证据链（2026-11-10）：`check-host` 并入 `verify-static`；detekt + ktlint + Android Lint 接入 `check-quality`（三份 baseline 起步，0 失败）；`make evidence-test` 生成 `20261109T163805Z-tests-pass`（65/65），`verify-claim` PASS；文档同步
- [ ] P5 验收（负向注入 + 冷启动首访 + 归档演练）

## 盘点结论

- 语言 / 构建：Kotlin + Compose + Hilt + Room + NDK/CMake（llama.cpp），`--language android`，建议测试命令 `./gradlew testDebugUnitTest`（已接 `scripts/verify-unit.sh`）。
- 现有门禁：接入前无 AGENTS/HARNESS/Makefile/CI/harness；`make check` / `verify-static` 为本次新增。
- 文档规模与索引缺口：10 篇 + README；缺 `docs/README.md` 索引（P1 已补临时索引，P2 蒸馏）；1 条跨仓断链（P1 已改文字）；6 处疑似过期标记（02/03/04 顶部横幅、09/10 待验证）。
- 卫生风险：`third_party/llama.cpp` 绝对符号链接；`/local/` 本机路径 3 个跟踪文件；4 个节流常量 + `debounceJobs`/`translationPackBody`/`indeterminate` 死代码；两个 debug Activity `exported=true`；`.gitignore` 缺 `.kotlin/`、`*.hprof`、`captures/`。
- 建议 profile 与 test 命令：standard；`./scripts/verify-unit.sh`（JUnit XML 由 P4 适配为证据）。

## 文档蒸馏映射

| 原文档 | 去向（重写 / 归档 `docs/_archive/` / 删除） | 理由 |
| --- | --- | --- |
| `01-product-prototype.md` | 重写 `docs/01-product.md`；原文归档 | 产品规则仍有效，需去实现期细节 |
| `02-architecture.md` | 重写 `docs/02-architecture.md`；原文归档 | 引擎名/类名与代码不一致，按代码重写 |
| `03-tech-choices.md` | 蒸馏 `docs/03-decisions.md`（D1..Dn 唯一决策表）；原文归档 | ML Kit 推演是历史，结论已是 SenseVoice/TranslateGemma |
| `04-implementation-principles.md` | 重写 `docs/04-runtime.md`；原文归档 | 流水线形状有效，引擎细节按代码校正 |
| `05-obstacles.md` | 当前约束并入 `03-decisions.md` 约束行 + `05-known-issues.md`；原文归档 | 阻碍多已解决，需保留仍成立的 |
| `06-compromises.md` | 并入 `docs/05-known-issues.md`；原文归档 | 当前取舍仍适用 |
| `07-roadmap.md` | 重写 `docs/06-roadmap.md`（Now/Next/Later）；原文归档 | 甘特已过期，进度权威是 active 计划 |
| `08-on-device-llm.md` | 校正后保留 `docs/07-on-device-llm.md`；原文归档 | 核心技术资产，需标数字日期/设备 |
| `09-current-state.md` | 拆出决策/问题；保留 `docs/09-current-state.md` 现状速览；原文归档 | 自指漂移（D-6 与 Git 历史不一致） |
| `10-latency-optimization.md` | 保留 `docs/08-latency.md`（数字标日期）；原文归档 | 核心资产，方案/状态表仍有效 |

## 清洁清单

- [x] 删除死代码：`TranslationPolicy` 4 个节流常量、`InterpretationViewModel.debounceJobs`、`Copy.translationPackBody`、`ManagedAssets.indeterminate` 及其 UI 分支（测试同步移除构造参数）；65 单测 PASS
- [x] debug Activity 移入 `app/src/debug/`（debug manifest overlay）：`processDebugMainManifest` 合并含两个入口，`processReleaseMainManifest` 为 0
- [x] `third_party/llama.cpp` 绝对符号链接删除：CMake 固定 tag `b10775` 走 `FetchContent`，本机可用 `LLAMA_CPP_SRC` 覆盖（不入库）
- [x] `gradlew.local.sh` → `scripts/gradlew-local.sh`：JDK/SDK 从环境/`local.properties` 读取，不再含机器路径；`scripts/verify-unit.sh` 同步
- [x] `prototype/platform.html` 已归档 `docs/_archive/prototype/`
- [x] `.gitignore` 补 `.kotlin/`、`*.hprof`、`captures/`
- [x] 桩代码决策清单已写入 `docs/05-known-issues.md`（实现/撤 UI/标未验证三选一，未在本轮实现）

## 传感器接线

| 传感器 | 命令 | 现状 | 目标 |
| --- | --- | --- | --- |
| 文档 / 指令门禁 | `python3 tools/check_docs.py`、`python3 tools/check_agents.py` | 已 PASS（P1） | 保持 0 |
| 计划状态 | `python3 tools/check_plan.py check` | 已 PASS（P1） | 保持 0 |
| 静态门禁总入口 | `make verify-static`（check + 证据 schema + check-host） | 已 PASS（P4） | 保持 0 |
| 宿主卫生检查 | `python3 tools/check_hygiene.py`（并入 check-host） | PASS（P3/P4） | 保持 0 |
| 分层守卫 | `python3 tools/check_layers.py`（并入 check-host） | PASS（72 文件 0 违规） | 保持 0 |
| 代码质量 | detekt + ktlint + Android Lint（`make check-quality`） | PASS（baseline 起步，0 失败） | 保持 0；新增问题失败 |
| 证据链 | `tools/evidence_from_junit.py` → `evidence.py` → `verify_claim`（`make evidence-test`） | 就绪（P4） | `tests-pass` 证据 PASS |
| 负向注入 | 手工注入矩阵（P5） | 待 P5 | 注入必红/恢复必绿 |

## 负向注入验收

- [ ] 删除一条文档索引行 → `check_docs.py` 变红，恢复后变绿
- [ ] 指令层违规（超预算 / 错 `§` 号 / 敏感串）→ `check_agents.py` 变红
- [ ] 跟踪构建产物/绝对符号链接/本机路径 → `check_hygiene.py` 变红
- [ ] 越层 import → `check_layers.py` 变红
- [ ] 删一个测试 → `unit.floor=65` 触发 `verify_claim` FAIL
- [ ] 证据缺失/陈旧 → `verify_claim.py` 非 PASS（exit 2 / 1）
- 记录每项一次「注入前 exit / 注入后 exit / 恢复后 exit」作为证据

## 验证证据

| 命令 | 结果 | 环境 | 证据ID |
| --- | --- | --- | --- |
| `make check`（P1 接入后） | PASS（exit 0） | Android 仓 `5179fdd` 工作树；python3 标准库 | —（过程记录：P1） |
| `make verify-static`（P1 接入后） | PASS（exit 0） | 同上 | —（过程记录：P1） |
| `./scripts/verify-unit.sh`（P1 复跑） | PASS（BUILD SUCCESSFUL；JUnit 65 用例基线） | 本机 JDK 17 / Gradle 8.10.2 | —（过程记录：P1；P4 前未生成证据 JSON） |
| `make check`（P2 文档蒸馏后） | PASS（exit 0；相对链接 164 条全部存在、围栏成对、docs 索引 18 个目标、公开文档 11/16、4 个指令文件预算内、敏感串 0） | Android 仓工作树；python3 标准库 | —（过程记录：P2） |
| `python3 tools/check_layers.py`（P3 后） | PASS（72 个 Kotlin 文件，0 分层违规；R1–R6） | 本机 python3 3.14 | —（过程记录：P3） |
| `python3 tools/check_hygiene.py`（P3 后） | PASS（155 个跟踪文件，0 违规：无绝对符号链接/本机路径/构建产物） | 同上 | —（过程记录：P3） |
| `:app:processDebugMainManifest` + `:app:processReleaseMainManifest` | PASS：debug 合并含 2 个 debug 入口，release 0；BUILD SUCCESSFUL 15s | JDK 17 / Gradle 8.10.2 | —（过程记录：P3） |
| `./scripts/verify-unit.sh`（P3 死代码/入口清理后） | PASS：BUILD SUCCESSFUL 27s；JUnit 65 | JDK 17 / Gradle 8.10.2 | —（过程记录：P3；P4 生成证据 JSON） |
| `make check-host`（P4） | PASS：分层 72 文件 0 违规；卫生 155 跟踪文件 0 违规 | 本机 python3 3.14 / git | —（过程记录：P4） |
| `make check-quality`（P4） | PASS：detekt + ktlintCheck + lintDebug；三份 baseline 生成，0 失败 | JDK 17.0.13 / Gradle 8.10.2 / AGP 8.7.2 | —（过程记录：P4） |
| `make evidence-test`（2026-11-10，clean tree @ `294a9f9`） | **PASS**：`./scripts/verify-unit.sh --rerun-tasks` 11s → 65 passed / 0 failed / 0 skipped → `evidence.py` 写入证据；`make verify-claim` → PASS | JDK 17.0.13 / Gradle 8.10.2 / AGP 8.7.2；JVM unit | `20261109T163805Z-tests-pass` |

## 未验证项

- 单测已在 P3 清理后复跑 PASS（65）；P4 取证时需 `--rerun-tasks` 生成 JUnit XML 证据。
- release APK 未重新构建（native 依赖需下载 llama.cpp 源码）；已用 manifest 合并任务验证 debug/release 差异。
- 质量基线为存量债记录（baseline 起步），不代表历史 findings 已修；新增问题会失败。
- `tests-pass` 证据为 JVM 单测（65）；真机与延迟仍未在本轮复跑，相关完成声明仍按 UNVERIFIED 处理。
- 真机（荣耀 ALP-AN00）未复跑；P3 清洁后需真机手测清单。
- Android Lint/detekt 首次噪音未知；P4 用 baseline 起步。
- 蒸馏后的历史数字（延迟/模型结构/自检）来自归档，本轮未复测；真机未复跑（P3 后手测）。

## 未提交改动

- 无未提交改动（tests-pass 证据已提交）。

## 下一步

1. 提交 P4（本计划 dirty 声明与本文件一致；提交后把本行改回「无未提交改动」）。
2. 生成并提交 `tests-pass` 证据：clean tree 上 `make evidence-test` → 证据文件提交 → 回填证据 ID → `make verify-claim` PASS。
3. P5 验收：负向注入（删 docs 行/越层 import/跟踪产物/删测试/脏树证据）→ 全红→恢复绿；冷启动首访；计划 done/归档演练。
