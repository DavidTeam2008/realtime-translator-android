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
    - gradlew.local.sh
    - third_party/
    - prototype/
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
- [ ] P2 文档蒸馏
- [ ] P3 清洁批次
- [ ] P4 传感器与证据链
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

- [ ] 删除死代码：`TranslationPolicy` 4 个节流常量、`InterpretationViewModel.debounceJobs`、`Copy.translationPackBody`、`AssetCard.indeterminate` 分支
- [ ] debug Activity 隔离（debug source set 或 `exported=false`），release 包不留入口
- [ ] `third_party/llama.cpp` 绝对符号链接改为固定 tag/相对方案，CONTRIBUTING 写复现步骤
- [ ] `gradlew.local.sh` 迁入 `scripts/`，路径改环境变量/本地覆盖；`/local/`、`/local/` 出库
- [ ] `prototype/platform.html` 归档到 `docs/_archive/prototype/`
- [ ] `.gitignore` 补 `.kotlin/`、`*.hprof`、`captures/`、`test-results`
- [ ] 桩代码决策清单（总结/音频策略/语言能力/下载）：实现、撤 UI 或标未验证

## 传感器接线

| 传感器 | 命令 | 现状 | 目标 |
| --- | --- | --- | --- |
| 文档 / 指令门禁 | `python3 tools/check_docs.py`、`python3 tools/check_agents.py` | P1 已 PASS | 保持 0 |
| 计划状态 | `python3 tools/check_plan.py check` | P1 已 PASS | 保持 0 |
| 静态门禁总入口 | `make verify-static` | P1 已 PASS | 保持 0 |
| 宿主卫生检查 | `python3 tools/check_hygiene.py`（P4） | 未接入 | 0（符号链接/本机路径/根白名单/大文件） |
| 分层守卫 | `python3 tools/check_layers.py`（P4） | 未接入 | 0（domain/services/features 依赖方向） |
| 代码质量 | detekt + ktlint + Android Lint（P4） | 未接入 | `make check-host` 0（baseline 起步） |
| 证据链 | `tools/evidence_from_junit.py` → `evidence.py` → `verify_claim`（P4） | 未接入 | `tests-pass` PASS |
| 负向注入 | `make sensors-selftest`（P5，宿主脚本） | 未接入 | 注入必红/恢复必绿 |

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

## 未验证项

- P1 单测为接入前实测基线（65 用例）；接入后仅复跑到 UP-TO-DATE，P4 取证时需 `--rerun-tasks` 重跑。
- 真机（荣耀 ALP-AN00）未复跑；P3 清洁后需真机手测清单。
- Android Lint/detekt 首次噪音未知；P4 用 baseline 起步。

## 未提交改动

- 无未提交改动（计划已提交）。

## 下一步

1. 提交本计划（dirty 声明与本文件一致）。
2. P2 文档蒸馏：先写 `docs/README.md`（当前 + `_archive` 双表），再按上方映射重写/归档。
3. P3 起按清单逐项提交（每项单独 commit），保持 65 单测全绿。
