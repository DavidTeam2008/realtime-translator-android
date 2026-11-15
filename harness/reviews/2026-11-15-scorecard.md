# harness 评分卡 · 2026-11-15

> 草稿：由 `make scorecard`（`tools/scorecard.py --generate`）生成；「自评」与「独立复评」两列需人工填写，生成器只提供门禁快照，不自动打分。
> **自评不是认证**；「独立复评」列为 TBD 时，本评分卡不算完成证据。
> 每次大改后重新生成；`make check` 会对过期评分卡给出 WARN（不阻断）。

- checkedAt: 2026-11-15T17:34:24Z
- commit: 2d6da0b（dirty 文件 3 个）
- kitVersion: 0.5.3
- evidence: tests-pass=20261115T173424Z-tests-pass（PASS）；docs-pass=20261115T173424Z-docs-pass（PASS）；static-gates=20261110T053949Z-static-gates（PASS）
- 测试基线：floor=65 expectedSkipped=0（harness/test-baseline.json）
- 文档计数：16 篇（docs/ + references/ + rootDocs 中现有文件）

## 1. 门禁快照（自动）

| 命令 | exit | 关键输出 |
| --- | --- | --- |
| `python3 tools/check_docs.py` | 0 | [OK] 相对链接：157 条全部存在；[OK] 代码围栏：22 篇文档成对；[OK] docs 索引：docs/README.md 已登记 19 个目标；[OK] 公开文档：根目录 md 白名单 5 项，公开文档 12 篇（上限 16）；[OK] token 预算：AGENTS.md ≈1190/1200（余 10） |
| `python3 tools/check_agents.py` | 0 | [OK] 指令文件：3 个存在（nestedMaxBytes=8192, nestedMaxTokens=1000）；[OK] 嵌套指令 token：docs/AGENTS.md ≈984/1000（余 16）；[OK] 嵌套指令 token：harness/AGENTS.md ≈640/1000（余 360）；[OK] token 预算：AGENTS.md ≈1190/1200（余 10）；[OK] token 预算：HARNESS.md ≈1451/1500（余 49） |
| `python3 tools/check_plan.py check --lenient-uncommitted` | 0 | [WARN] harness/plans/_archive/2026-11-10-android-adoption.md  status=done（归档；strict 下 FAIL）；[WARN] submitted commit 2c3b479 早于计划文件（或计划不在该提交中）；用当前 scope 审计，存在提交后放宽 allow 的风险；[WARN] harness/plans/_archive/2026-11-10-kit-v023-upgrade.md  status=done（归档；strict 下 FAIL）；[WARN] submitted commit 0fd697c 早于计划文件（或计划不在该提交中）；用当前 scope 审计，存在提交后放宽 allow 的风险；[WARN] submitted commit 48496f7 早于计划文件（或计划不在该提交中）；用当前 scope 审计，存在提交后放宽 allow 的风险 |
| `python3 tools/check_hygiene.py` | 1 | [OK] 本机路径扫描：扫描 145 个跟踪文件 / 跳过 19（docs/_archive/=12、harness/config.json=1、harness/plans/=3、harness/reviews/=1、tools/check_agents.py=1、tools/check_hygiene.py=1）；[FAIL] 根目录文件不在 hygiene.rootAllowlist：.harness-manifest.json；[FAIL] check_hygiene 发现 1 个卫生问题（exit 1） |
| `python3 tools/check_layers.py` | 0 | [OK] 分层检查来源：git 跟踪（git ls-files）｜扫描 70 个源文件（tracked 70 / untracked 0；排除 0 个文件 / 0 个目录）；[OK]   规则 domain：eligible=70 matched=13 violations=0；[OK]   规则 services：eligible=70 matched=33 violations=0；[OK]   规则 features：eligible=70 matched=15 violations=0；[OK]   符号守卫 engine：eligible=31 matched=0 violations=0 |
| `python3 tools/verify_claim.py --all` | 1 | CLAIM 20261115T173424Z-docs-pass: UNVERIFIED — command exit 0：python3 tools/check_docs.py；证据文件未被 git 跟踪（CI 无法复核）；CLAIM 20261115T173424Z-tests-pass: UNVERIFIED — passed=65≥unit.floor=65，failed=0，skipped=0==unit.expectedSkipped；已从 16 个 JUnit XML 重算；证据文件未被 git 跟踪（CI 无法复核）；artifact 未被 git 跟踪：harness/evidence/artifacts/20261115T173424Z-1-TEST-com.duiyi.android.domain.CaptionModelsTest.xml；artifact 未被 git 跟踪：harness/evidence/artifacts/20261115T173424Z-2-TEST-com.duiyi.android.domain.ManagedAssetRulesTest.xml；artifact 未被 git 跟踪：harness/evidence/artifacts/20261115T173424Z-3-TEST-com.duiyi.android.domain.PaneStateTest.xml；artifact 未被 git 跟踪：harness/evidence/artifacts/20261115T173424Z-4-TEST-com.duiyi.android.domain.SpokenTextNormalizeTest.xml；artifact 未被 git 跟踪：harness/evidence/artifacts/20261115T173424Z-5-TEST-com.duiyi.android.domain.TranslationPolicyTest.xml；artifact 未被 git 跟踪：harness/evidence/artifacts/20261115T173424Z-6-TEST-com.duiyi.android.domain.routing.LanguageRouterTest.xml；artifact 未被 git 跟踪：harness/evidence/artifacts/20261115T173424Z-7-TEST-com.duiyi.android.domain.routing.SpokenSegmentJoinerTest.xml；artifact 未被 git 跟踪：harness/evidence/artifacts/20261115T173424Z-8-TEST-com.duiyi.android.domain.routing.StablePrefixTrackerTest.xml；artifact 未被 git 跟踪：harness/evidence/artifacts/20261115T173424Z-9-TEST-com.duiyi.android.domain.routing.UtteranceAssemblerTest.xml；artifact 未被 git 跟踪：harness/evidence/artifacts/20261115T173424Z-10-TEST-com.duiyi.android.services.persistence.InMemoryTaskStoreTest.xml；artifact 未被 git 跟踪：harness/evidence/artifacts/20261115T173424Z-11-TEST-com.duiyi.android.services.speech.SenseVoiceTextTest.xml；artifact 未被 git 跟踪：harness/evidence/artifacts/20261115T173424Z-12-TEST-com.duiyi.android.services.speech.SherpaModelSpecTest.xml；artifact 未被 git 跟踪：harness/evidence/artifacts/20261115T173424Z-13-TEST-com.duiyi.android.services.speech.SpeechEnginePolicyTest.xml；artifact 未被 git 跟踪：harness/evidence/artifacts/20261115T173424Z-14-TEST-com.duiyi.android.services.speech.SpeechTextRouterTest.xml；artifact 未被 git 跟踪：harness/evidence/artifacts/20261115T173424Z-15-TEST-com.duiyi.android.services.translation.GemmaModelSpecTest.xml；artifact 未被 git 跟踪：harness/evidence/artifacts/20261115T173424Z-16-TEST-com.duiyi.android.services.translation.TranslateGemmaPromptTest.xml（CI 无法复核）；结论：FAIL（0 PASS / 1 FAIL / 3 UNVERIFIED） |

## 2. 五子系统评分（自评 / 独立复评）

| 子系统 | 关注点 | 自评（1–5） | 独立复评（1–5） | 证据 |
| --- | --- | --- | --- | --- |
| Instructions | 根 / 嵌套指令、预算、引用可解析 | TBD | TBD | make check / check_agents |
| State | 计划状态机、handoff、唯一 active、证据绑定 | TBD | TBD | check_plan / verify_claim |
| Verification | 静态 / 动态门禁、证据三值、skip 白名单 | TBD | TBD | 门禁快照 / verify_claim |
| Scope | 改动范围声明、越界拦截、DoD | TBD | TBD | check_plan / scope.allow |
| Session Lifecycle | 冷启动、健康检查、收尾与交接 | TBD | TBD | make status / handoff |

## 3. 未验证 / 待人工

- 五子系统分数为 TBD：需人工按 1–5 口径（1 缺失 / 3 有规则不可机检 / 5 有门禁+证据+定期复核）自评；
- 自评不是认证；独立复评列为 TBD 时本卡不算完成证据（release 门禁可另行强制）。
- 独立复评需由未参与实现的人/Agent 只读仓库后填写；自评与独立复评分列，不互相替代。
- 门禁快照只证明「命令跑了、退出码如此」，不证明行为正确；动态/真机/性能仍需项目自己的证据。

## 4. 复现

```bash
make scorecard          # 重新生成本文件
make verify-static      # 静态门禁
make selftest           # 负向注入自检（证明门禁会红）
make verify-claim       # 证据三值判定
```
