---
id: 2026-11-16-upgrade-harness-kit-0-5-3
status: done
level: L2
owner: david
updated: 2026-11-16
submitted: 2d6da0b,1b75266
scope:
  allow:
    - harness/plans/_archive/2026-11-16-upgrade-harness-kit-0-5-3.md
    - .harness-manifest.json
    - .github/
    - .gitignore
    - .githooks/
    - AGENTS.md
    - CONTRIBUTING.md
    - HARNESS.md
    - Makefile
    - docs/
    - harness/
    - references/
    - tools/
  deny:
    - app/
    - gradle/
    - prototype/
    - third_party/
    - build.gradle.kts
    - settings.gradle.kts
    - gradle.properties
    - local.properties
acceptance:
  - harness-upgrade --plan 收敛为 SAME/LOCAL_ONLY（无 UPGRADE/CONFLICT/ADD/OBSOLETE）
  - make check 退出 0
  - make verify-static 退出 0
  - make verify-claim 退出 0（tests-pass / static-gates / docs-pass 三条 claim）
  - make selftest PASS（负向注入全拦截）
  - make verify-all PASS
verify:
  - make verify-static
  - make selftest
---

# 2026-11-16-upgrade-harness-kit-0-5-3 · Android 仓执行计划

> 计划是跨会话任务的进度真源：中断 / 交接前更新，完成后归档。
> 根指令见 [`../../AGENTS.md`](../../AGENTS.md)，流程见 [`../../references/workflow.md`](../../references/workflow.md)，证据格式见 [`../evidence/README.md`](../evidence/README.md)。

## 目标与非目标

- 目标：把 Android 仓从 harness-kit **0.2.3** 跨级升级到已发布 tag **0.5.3**：按 kit playbook 的「版本升级 + v0.2.x → v0.3/v0.4/v0.5 迁移矩阵」回写 kit 管理面，人工保留宿主文档（AGENTS/CONTRIBUTING/HARNESS/docs/references 的宿主版本），首次建立 `.harness-manifest.json` 基线，迁移证据到 v0.4+ 格式，门禁与负向注入全绿。
- 非目标：不改 app 业务代码与单测；不重跑全量 JVM 单测（本机无 Android SDK，见未验证项）；不做真机/延迟复测；不升级 profile（仍 standard）。

## 验收

- [x] `harness-upgrade --plan` 收敛为 **SAME=23 / LOCAL_ONLY=11**（无 UPGRADE/CONFLICT/ADD/OBSOLETE）
- [x] `make check` 退出 0
- [x] `make verify-static` 退出 0（含归档计划 strict、证据 schema、hygiene/layers）
- [x] `make verify-claim` 退出 0（3 PASS / 0 FAIL / 0 UNVERIFIED；旧 tests-pass 归档并由新证据 `supersedes`）
- [x] `make selftest` **9 PASS / 0 FAIL / 0 SKIP**
- [x] `make verify-all` PASS

## 改动范围

- 允许：kit 管理面（front matter scope.allow）+ 宿主文档最小适配（HARNESS 预算压缩、docs/README 压缩、docs/AGENTS 压缩、config 迁移）。
- 禁止：`app/`、`gradle/`、构建脚本与 `local.properties`；不新增 kit 外管理约定。

## 升级决策（0.2.3 → 0.5.3）

- 基线：旧仓无 `.harness-manifest.json`（v0.2.13 前接入），按 legacy 路径渲染 0.5.3 后逐文件比对（v0.2.3 参考树对比确认宿主自定义文件）。
- 整文件回写（kit 管理面）：`tools/` 全部脚本（含新增 `harness.py` / `harness_selftest` / `scorecard.py`）、`harness/AGENTS.md`、`harness/README.md`、`harness/evidence/{README,TEMPLATE,schema}`、`harness/plans/_template.md`、`harness/requirements/_template.md`、`.github/workflows/verify.yml`（`fetch-depth: 0`）、`.githooks/pre-push`、`docs/harness-scorecard.md`。
- Makefile：换 v0.5.3 kit 目标段（status/start/verify/handoff/check-plan-strict/verify-all/selftest/upgrade-check/scorecard）并保留宿主目标（check-quality / test / evidence-test）。
- config：`kitVersion` 0.5.3、`nestedMaxTokens`、`docs/README.md`/`HARNESS.md` 预算、`scorecard` 段、tests-pass `requireArtifact=true`、白名单加 scorecard；保留宿主预算（AGENTS 1200 / contracts 700 / verification 900）、hygiene/layers；`.harness-manifest.json` 加入 `hygiene.rootAllowlist`。
- 宿主文档（保留内容、按新预算压缩）：`HARNESS.md` 1451/1500（§5 更新为 0.5.3 升级流程）、`docs/README.md` 846/1000（登记 11 篇 docs + scorecard）、`docs/AGENTS.md` 984/1000；`AGENTS.md` 1190/1200、`CONTRIBUTING.md`、`references/*` 保持宿主版本。
- `.gitignore`：kit 追加块换 android 语言块（`.gradle/`、`local.properties`），保留宿主 Kotlin 诊断条目。
- 首次 `.harness-manifest.json`：33 个文件 + append `templateSha256`，宿主自定义文件在 plan 中显示 LOCAL_ONLY。
- 证据迁移（v0.4+ 要求）：tests-pass 由既有 `app/build/test-results` JUnit XML 经新版 `evidence_from_junit.py` 脱敏复制入库并重算（65/0/0），旧证据归档并 `supersedes`；新增 docs-pass 证据；static-gates 沿用既有 PASS 证据（static claim 每次复跑命令）。归档 done 计划补「未验证豁免」表。

## 进度

- [x] 基线：`make check` / `verify-static` PASS（HEAD a6e491b，工作树 clean）
- [x] v0.5.3 tag 渲染到临时目录，与 v0.2.3 参考树逐文件比对，区分 kit 管理面与宿主自定义
- [x] 应用回写 + config/Manifest/Makefile/.gitignore 迁移
- [x] 收敛 `--plan` SAME=23 / LOCAL_ONLY=11；`make check` / `verify-static` PASS
- [x] 证据迁移与 gate 修复（hygiene rootAllowlist、scorecard 草稿）
- [x] 提交 `2d6da0b`（升级）+ `1b75266`（证据）；本计划归档为第三个提交
- [x] `make selftest` 9/9、`make verify-all` PASS

## 验证证据

| 命令 | 结果 | 环境 | 证据ID |
| --- | --- | --- | --- |
| `harness-upgrade --plan`（kit v0.5.3 tag） | 退出 0；SAME=23 / LOCAL_ONLY=11，无 UPGRADE/CONFLICT/ADD/OBSOLETE | local/darwin，HEAD 2d6da0b | —（过程记录：只读，未写目标仓） |
| `harness-upgrade --check`（kit v0.5.3 tag） | 版本一致；仅 11 个已声明 LOCAL_CHANGED（宿主定制） | local/darwin，HEAD 2d6da0b | —（过程记录：宿主定制保留） |
| `make check` | PASS（0 error；归档计划历史 WARN） | local/darwin | —（过程记录：exit 0） |
| `make verify-static` | PASS（含计划 strict / 证据 schema / hygiene / layers） | local/darwin | —（过程记录） |
| `make verify-claim` → tests-pass | PASS（passed=65，failed=0，skipped=0；16 个 XML 独立重算） | local/darwin，HEAD 2d6da0b | 20261115T173424Z-tests-pass |
| `make verify-claim` → docs-pass | PASS（check_docs exit 0） | local/darwin，HEAD 2d6da0b | 20261115T173424Z-docs-pass |
| `make selftest` | PASS（M1–M9 全拦截：9 PASS / 0 FAIL / 0 SKIP） | local/darwin，clean tree 1b75266 | —（过程记录：负向注入矩阵） |
| `make verify-all` | PASS（静态门禁 + 三值判定） | local/darwin | —（过程记录） |
| `python3 tools/check_docs.py`（升级后） | PASS（22 篇文档、19 索引目标、预算全过） | local/darwin，HEAD 2d6da0b | 20261115T173424Z-docs-pass |
| tests-pass（既有 JUnit 迁移） | PASS（passed=65 ≥ floor 65，failed=0，skipped=0；16 个 XML 脱敏复制后重算） | local/darwin，HEAD 2d6da0b | 20261115T173424Z-tests-pass |
| static-gates（沿用 2026-11-10 证据） | PASS（static claim 每次复跑 `make verify-static`） | local/darwin / v0.2.3 时期 | —（过程记录：20261110T053949Z-static-gates） |

## 未验证项

- 本机无 Android SDK（`local.properties` 的 `sdk.dir` 指向不存在的卷），JVM 单测**未重跑**：tests-pass 由既有 `app/build/test-results` JUnit XML 迁移并独立重算，需在具备 SDK + JDK 17–21 的机器上用 `make test` / `make evidence-test` 复跑确认。
- 真机（荣耀 ALP-AN00）与真机延迟未复跑：沿用历史归档数字，本轮未做真机验证。
- `make check-quality`（detekt + ktlint + Android Lint）未运行（需 SDK），质量 baseline 未复核。
- release APK 未重新构建（native 依赖需下载 llama.cpp 源码），沿用历史结论。

## 未验证豁免（done 前有未验证项时必须填）

| 项目 | 理由 | 负责人 | 到期日 |
| --- | --- | --- | --- |
| 本机无 Android SDK | 证据由既有 JUnit 迁移并独立重算；升级不触碰 app/ 与测试代码，静态与负向门禁已覆盖升级面 | david | 2026-12-31 |
| 真机（荣耀 ALP-AN00）与真机延迟未复跑 | 需真机与手测清单；本轮只做 kit 升级，业务代码零改动 | david | 2026-12-31 |
| make check-quality | 需 Android SDK；质量门禁为本地执行边界，本轮未扩大范围 | david | 2026-12-31 |
| release APK 未重新构建 | native 依赖需下载 llama.cpp 源码；沿用历史构建结论 | david | 2026-12-31 |

## 未提交改动

- 无未提交改动（已提交 2d6da0b 升级 + 1b75266 证据；本计划归档为第三个提交，不列入 submitted 以避免 scope 同批审计）

## 下一步

1. 在具备 Android SDK 的机器上 `make test` + `make evidence-test` 复跑单测并刷新 tests-pass 证据。
2. 真机（荣耀 ALP-AN00）复测听写/翻译/延迟，结果写回 `docs/08-latency.md` 与计划。
3. 如需推送：`git push origin main` 后确认 GitHub Actions `verify`（已带 `fetch-depth: 0`）首次运行结果。
