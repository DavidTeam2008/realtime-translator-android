# harness-kit 接入评估 · 对译 Duiyi Android

> 状态：**评估稿（未执行）**；本文件未纳入 Git，确认后可转为 `harness/plans/` 正式计划或直接删除。
> 评估对象：`~/Documents/code/ios/realtimeTranslatorMultiple/realtimeTranslatorAndroid`（remote `DavidTeam2008/realtime-translator-android`，main `2ff1fae`）
> 评估基准：仓库只读盘点（2026-11-09）+ 单测基线实跑 + `harness-kit` 0.2.1 契约（`VERSION`/`SPEC.md`/`profiles/*.json`/`docs/playbook.md`）
> 补充（2026-11-09 晚）：决策前问答见 §0.1；kit v0.2.2/v0.3.0 泛化提案见附录 C。
> 本次评估未改动任何跟踪文件；唯一副作用是跑了一次 `./gradlew.local.sh testDebugUnitTest`（产物写 `app/build/`，已被忽略）。

---

## 0. 结论速览（先回答"改造后这些问题还在不在"）

**一句话**：harness-kit 能把"靠人记得"变成"机器能拦"，**但只覆盖它管得到的层**——文档结构/链接/索引/预算、计划唯一真源、证据可证伪、推送与 CI 门禁。你列的三类问题里：**文档混乱（结构性）会被门禁消除；过程文件/进度不直观会被状态层+卫生门禁大幅压低；文档"内容过期"和"代码不简洁"kit 本身不解决**，必须补 Android 侧传感器（detekt/lint/分层守卫/docmap）并保留人的收尾纪律。

| 你列的问题 | 接入 kit 后的命运 | 真正起作用的机制 | 残留风险 |
| --- | --- | --- | --- |
| 文档混乱（无索引、重复、断链、双真源） | **大部分消除（机器可判部分）** | `docs/README.md` 唯一索引 + `check_docs`（链接/围栏/索引/公开文档/预算）+ 根 `AGENTS.md` 路由 | 内容组织仍需一次蒸馏重构（§2.4；"登记齐全但内容重复"门禁不拦） |
| 过程文件与文档不清理、进度不直观 | **大幅降低**（进度变成一屏可读的 active 计划+证据） | `harness/plans/` 唯一 active + `check_plan`；evidence 三值 + clean-tree 绑定；`resume`/`handoff`；pre-push/CI | kit **不扫**根目录杂项/被跟踪的构建产物/绝对符号链接——需补宿主 `check_hygiene` 传感器 |
| 无用文件不清理、代码不简洁 | **不解决（kit 明确不管宿主代码质量）** | 只有 scope 约束 + 测试只增不减基线 | **高残留**；必须加 detekt/ktlint/Android Lint/分层守卫/死代码扫描，否则原样保留 |
| 文档不及时更新（架构/选型变了文档不更新） | **部分解决**：从"不可见"变"显式状态+变更清单"，语义正确性仍需人/agent 保证 | 决策表唯一 ID、文档状态字段（当前/历史）、计划 DoD 的文档影响清单、收尾审计、docmap 变更门禁 | **中残留**；语义过期（数字/结论/命令）无法自动判定 |
| 其他：环境不可复现（`/local/` 符号链接、本机脚本入库） | **可拦住新增**，存量需一次清理 | `sensitivePatterns` + hygiene 传感器 + CONTRIBUTING 环境章节 | 低 |
| 其他：桩/未实现功能被当完成（HonestSummarizer 等） | **可显式化为 UNVERIFIED**，不能自动补实现 | 三值证据 + 计划"未验证项" + 验收判据 | 中（产品决策问题，非工具问题） |
| 其他：测试面窄、无 CI、无静态分析 | **部分**：kit 只做静态链路；动态/真机仍是宿主责任 | CI adapter（静态）+ claims + test-baseline；动态测试需自建 | 中 |

**判断依据**：kit 自身 README 写明"不替你写测试命令、不做 CI 平台、不保证接入即通过"；`check_docs` 只校验**结构与可机械判定的部分**（见 §2.4 源码），`playbook.md` 也明确"语义过期靠流程与评审"。所以正确答案不是"接入=问题消失"，而是"接入=问题会在门禁上暴露，且新增问题更难溜过去"。

### 0.1 三个前置问题的回答（2026-11-09 补充）

| 问题 | 结论 | 落点 |
| --- | --- | --- |
| **Q1** 独立仓 pinned、不 vendor 进 Android 仓，对 Android 支持是否必要？ | **必要，但要拆成"消费线"和"开发线"**：宿主仓（Android）只**消费**已发布版本并记录 `kitVersion`；Android 支持（`android` 语言探测、JUnit 适配、brownfield 工具）在 **kit 上游**开发、测试、发版，再由 Android 仓 pin 新 tag。**不要在 Android 仓里改 kit / vendor / fork**——否则两套 kit 漂移、kit 卫生测试失效、升级无路径。备选：git submodule pin tag（可离线，仍是"引用"而非"复制"）；从 iOS 仓 `cp -r` 只作离线应急。 | §2.2、附录 C |
| **Q2** 这个 Android 改造场景能泛化出什么补进 kit？ | **能，而且比"空白试点"更有价值**：存量项目接入（adopt/inventory）、文档状态策略与变更映射门禁、通用卫生门禁、JUnit XML→证据适配器、负向注入（门禁自测）范式、brownfield playbook。分版本落地：**v0.2.2 接入能力**（adopt + android + JUnit + playbook），**v0.3.0 传感器能力**（statusPolicy / check_docmap / check_hygiene / sensors-selftest）。 | 附录 C |
| **Q3** 01–08 架构/选型是核心资产，怎么处理？ | **同意"蒸馏"而非只贴历史标签**：`docs/` 重写为**当前真源**（产品/架构/决策/运行时/已知问题/路线/端侧 LLM/延迟）；原文归档到 `docs/_archive/`（不改写、只加日期与状态头、不作现状引用）；**核心结论提炼为 `docs/03-decisions.md` 的 D 行**与已知问题/取舍条目，全部标"来源 `_archive/xx@date`"。 | §2.4 |

---

## 1. 现状盘点（基于实测，不是印象）

### 1.1 仓库基本盘

| 项 | 实测值 | 取证 |
| --- | --- | --- |
| 跟踪文件 | 115 个；3 个 commit（`440294c` 初始 / `1c3bcce` 卫生 / `2ff1fae` 延迟） | `git ls-files \| wc -l`、`git log` |
| 源码 | 86 个源文件（Kotlin + 1 个 `llama_jni.cpp`），Kotlin **10,815 行** | `find app/src -name '*.kt' \| xargs wc -l` |
| 单测 | 13 个测试文件 / 16 个测试类 / **65 个用例，0 失败 0 跳过，49s 通过** | 2026-11-09 实跑 `./gradlew.local.sh testDebugUnitTest` + JUnit XML 统计 |
| 测试面 | 仅 JVM 单测；**无 `app/src/androidTest`**（无 instrumented/UI 测试）、无延迟自动化 | `find app/src -maxdepth 2` |
| 文档 | README 2,133 tokens + `docs/01–10` 共 **2,351 行 / 36,645 tokens** | kit `token_estimate.py` 实算 |
| 工程门禁 | **无** `AGENTS.md`、`HARNESS.md`、`CONTRIBUTING.md`、`Makefile`、`harness/`、`.github/` | `ls` 全部 not found |
| 静态分析 | 无 ktlint / detekt / Android Lint 接线；无 CI | `app/build.gradle.kts`、无 workflow |

### 1.2 三类问题的实证

#### A. 文档混乱与过期

1. **无索引**：没有 `docs/README.md`；索引靠 `README.md` 里一张手写"时效"表维护，表本身把 `03`、`04` 标成 ❌，`02`、`07` 标成 ⚠️ —— 说明作者已经在人工兜底。
2. **断链 1 条（且跨仓库、本机路径）**：`docs/01-product-prototype.md:10` 链接到 `../../../realtimeTranslatorOptimize/docs/09-platform-prototype.md`，在当前机器之外必然 404。
3. **过期内容 61 处**：`docs/02–08` 仍大量写 **ML Kit / 系统 `SpeechRecognizer` / Gemini Nano**，而代码实际是 **sherpa-onnx SenseVoice + llama.cpp TranslateGemma**（`grep -c` 统计 61 行）。
4. **"过期后人工打补丁"的物证**：`docs/02/03/04` 顶部都加了"⚠️ 本文写于实现之前……以 `09-current-state.md` 为准"的横幅；`docs/09` 开头声明"本文是代码的实况"，并列出 9 行"与原设计的偏差"表。**这恰恰说明机制缺位**：文档不是没写，是写完没人能保证它跟着代码走。
5. **"当前状态"文档自己也已漂移**：
   - `docs/09` §6 D-6 写"`app/.cxx/`（395 个中间产物）**被提交进了 git**"，但当前 3 个 commit 的历史中 `.cxx` **从未被跟踪**（`git ls-tree -r 440294c | grep -c cxx` = 0，无删除提交）；`1c3bcce` 提交信息称"从索引移除"，实际 diff **只改了 `.gitignore`**。过程记录与 Git 历史不一致。
   - `docs/09` 说 D-1 "已修（待真机验证）"，README 第 116 行说"尚未编译与真机验证"——两处口径不一致。
6. **同一状态在三处重复**：README「当前状态」、`docs/09` §5/§6、`docs/10` §9 实施状态表，各写一遍进度，天然漂移。
7. **本机路径入库**：`/local/...` 出现在 `README.md`、`docs/09-current-state.md`、`gradlew.local.sh` 三个跟踪文件里。
8. **路线图与代码脱节**：`docs/07-roadmap.md` 的甘特图仍是 9 月计划，里程碑"M1–M5 代码路径已落地"但无日期/证据/验收记录；M5 验收"真机清单"从未签字。

#### B. 过程文件 / 进度不直观 / 无用文件

1. **进度只在文档与 commit message 里**：没有计划文件、没有证据文件、没有 CI 记录；"第 0–4 步代码已落地但尚未编译验证"这种关键状态散落在 README/09/10 三处。
2. **卫生历史与记录不符**：见 A.5；`app/.cxx` 当前本地 **1.4 GB / 644 个文件**、`app/build` **903 MB**，虽已忽略，但 `.gitignore` 仍缺 `.kotlin/`、`*.hprof`、`captures/`。
3. **不可复现的环境事实入库**：`third_party/llama.cpp` 是跟踪的绝对符号链接（mode `120000` → `/local/src/llama.cpp`，该目录非 git 仓库、无 tag）；换机静默走 `FetchContent` 下载 tag `b10775`，与实编译版本不一致。
4. **机器相关脚本入库**：`gradlew.local.sh`（本机 JDK/SDK 路径 shim）在仓库根；`local.properties` 已忽略，但 README 写死 `/local/...`。
5. **调试入口进 release**：`AndroidManifest.xml:34,39` 两个 debug Activity `android:exported="true"`，无 debug source set 隔离。
6. **确认的死代码**（2026-11-09 逐项 grep）：
   - `TranslationPolicy` 的 4 个节流常量（`FIRST_TRANSLATION_MS`/`TRANSLATION_MS`/`VOICE_FIRST_MS`/`VOICE_NEXT_MS`）**只有定义、零引用**；
   - `InterpretationViewModel.debounceJobs` 只 remove/clear、**从未 put**；
   - `Copy.translationPackBody` **零引用**；
   - `AssetCard.indeterminate` 生产代码只在 `ModelsScreen` 读取，`indeterminate=true` 只出现在测试。
7. **桩代码与正面宣传并存**（`docs/09` §1 已诚实记录，但产品面未收敛）：`HonestSummarizer` 恒 `DeviceNotEligible`、`AudioSessionPolicy` 三个 use case 同构、`DeviceCapabilityProbe` 语言集合恒空、`DeviceAssetCatalog` 写死 English。

#### C. 文档更新机制缺失

- 现状是"过期后补横幅/补偏差表"，而不是"变更时必须更新"。没有：
  - 决策唯一表（选型结论散在 `docs/03`、`docs/09` §1、`docs/10` §5，互相引用但无 ID/状态）；
  - 文档状态字段（当前/历史）——所以 `docs/01–08` 既是"设计史"又可能被当现状读；
  - "改代码→改哪些文档"的映射与检查；
  - 收尾/交接时的强制回写动作（计划、证据、文档三件事没有绑定）。

### 1.3 公平评价（这些是已有的优点，方案应保留）

- 文档投入在个人项目里属于高水位：`docs/09` 偏差表、`docs/10` 延迟归因与执行顺序、`docs/05/06` 阻碍/妥协记录，都是可复用的资产；
- README 综合质量不低：技术栈、真机策略、工具链坑（Gradle 8.14.5/JBR 25 不兼容）、诊断命令都写了；
- 已有 65 个单测且全绿，`domain/routing/speech policy` 这些高价值逻辑有覆盖；
- 作者已经在做"诚实记录"（D-1~D-6、桩代码清单），只是**没有机制把诚实记录变成门禁**。

> 结论：问题不是"文档写得差"，而是**没有单一真源、没有状态机、没有传感器**。这正是 harness-kit 的射程，但射程边界必须说清楚（见 §3）。

---

## 2. 方案：harness-kit 接入 Android 仓

### 2.1 目标与非目标

**目标**
1. 冷启动可恢复：任何 agent/人只读仓库就能回答"现在做到哪、下一步、哪些没验证"（一屏 = active plan + evidence + `resume`）。
2. 文档可机械校验：索引齐全、链接有效、围栏成对、公开文档收敛、token 预算内、指令层不漂移。
3. 完成可证伪：`unit-tests-pass` / `static-pass` / `lint-pass` 由证据 JSON + 三值判定，无 evidence id 一律按未验证。
4. 变更不越界、不假绿：pre-push + CI 跑静态门禁；证据要求 clean tree 且绑定 commit。
5. 为 kit 提供**真实项目外部试点**（此前只有空白 Python/Node/SwiftPM 试点），把 Android 卡点回写 kit。

**非目标**
- 不重写业务逻辑；不在本轮做性能优化/功能补齐（桩代码只做"实现或撤掉 UI"的决策清单）。
- 不把 kit 当运行时依赖；不引入第三方库；kit 产物全部可删。
- 不承诺"接入后文档语义永不过期"（见 §3 残留风险）。

### 2.2 档位、kit 来源与两阶段接入

| 决策 | 建议 | 理由 |
| --- | --- | --- |
| profile | **standard** | 有真实测试（65 个）+ 需要计划/证据/CI 防盗绿；minimal 不够（无计划/证据），strict 的 scorecard/reviews/release-check 可等发布前再升 |
| 语言 | v0.2.2 起 `--language android`；过渡期先 `--language other --test-command "./scripts/verify-unit.sh"` | kit 现有 `detect_language` 不识别 Gradle/AGP（只回退 `other` 并建议 `make test`）；Android 探测随 v0.2.2 进上游（附录 C·C2） |
| kit 消费 | **独立仓 pinned**（tag → `harness/config.json` 的 `kitVersion`），**不 vendor** | 单上游、可追溯；升级 = 换 tag + dry-run 人工合并；vendor 会造成双源漂移、kit 卫生测试失效、升级无路径 |
| kit 开发 | **所有 Android/brownfield 能力在 kit 上游做**，用本 Android 仓做只读试点 | 不在宿主仓 fork；新能力必须带 kit 测试、更新 SPEC/CHANGELOG、`make kit-publish` 同步独立仓 |
| 备选 | git submodule pin tag（离线可复现，仍是"引用"）；从 iOS 仓 `cp -r harness-kit/` 仅作离线应急 | vendor 是最后手段，需接受"双源 + 升级靠人工" |

**两阶段推进**（避免"先接 0.2.1 再升 0.2.2"的两次接入）：

- **Stage A · kit v0.2.2 先行**（在 kit 仓）：实现附录 C 的 C1/C2/C3/C4/C8（adopt CLI、android 探测、JUnit 适配器、brownfield playbook、改造计划模板）；以本 Android 仓做**只读**盘点试点；`make kit-check` 全绿、卫生扫描 0 命中、镜像仓发布 v0.2.2。
- **Stage B · Android 仓接入**：pin v0.2.2 → `harness-adopt` 出盘点报告与改造计划草稿 → `harness-init --profile standard --language android` → 进入 §4 的 P1–P5。

> 为什么 Stage A 先行：kit 的"升级/存量改造"路径本身未在真实项目验证（`docs/playbook.md` 明说），而 v0.2.1 对 Android 只能 `other` 兜底。用 Android 仓做 **首个真实 brownfield 试点 + 首个真实升级试点**，把卡点回写 kit，比两次手工迁移更省。

接入命令（Stage B，先 dry-run；kit v0.2.2 发布后）：

```bash
# 0) 取 kit（独立仓 pinned；网络不可用时改用 iOS 仓 harness-kit/ 目录同源拷贝）
git clone --depth 1 --branch v0.2.2 https://github.com/DavidTeam2008/harness-kit.git /tmp/harness-kit

# 1) 只读盘点（新能力：不改文件，输出改造建议 + 文档索引草稿 + 计划草稿）
cd /path/to/realtimeTranslatorAndroid
python3 /tmp/harness-kit/scripts/harness-adopt --target . --report /tmp/android-adoption.md

# 2) 正式 init（先 --dry-run 读 CREATE/CONFLICT 计划）
python3 /tmp/harness-kit/scripts/harness-init \
  --profile standard --target . --name "对译 Duiyi Android" \
  --language android --test-command "./scripts/verify-unit.sh" --dry-run
# 去掉 --dry-run 执行；init 结束会跑首次 make check 并透传退出码
```

> 目标仓当前**没有 Makefile**，所以 kit 会直接生成 `Makefile`（不是 `Makefile.harness`）；后续自定义目标用 `include` 或在该 Makefile 的 `check` 里追加。


### 2.3 改造后目录（新增/调整）

```text
realtimeTranslatorAndroid/
├── AGENTS.md                  # 根指令：路由 + 铁律（≤1200 tokens）
├── HARNESS.md                 # 五子系统在本仓的落地矩阵
├── CONTRIBUTING.md            # 环境（JDK17-21/Gradle 8.10.2/AS JBR25 坑）、单测/真机、证据流程
├── Makefile                   # check / verify-static / verify-claim / plan / check-host
├── docs/
│   ├── README.md              # 唯一索引：当前文档 + 历史档案两张表
│   ├── AGENTS.md              # 文档增量规则：状态字段、单真源、历史不改写
│   ├── 01-product.md          # 当前：产品规则 / 任务语义
│   ├── 02-architecture.md     # 当前：实际分层、模块注册、运行时、并发、存储
│   ├── 03-decisions.md        # 当前：唯一决策表 D1..Dn（含约束/风险行）
│   ├── 04-runtime.md          # 当前：实现原理（流水线/路由/TTS/持久化/模型准备）
│   ├── 05-known-issues.md     # 当前：已知缺陷、妥协、桩状态（D-1..D-6 收敛）
│   ├── 06-roadmap.md          # 当前：Now/Next/Later（链接 active 计划）
│   ├── 07-on-device-llm.md    # 当前：端侧 LLM 核心技术资产（数字标日期/设备）
│   ├── 08-latency.md          # 当前：延迟归因与优化状态（原 10 蒸馏）
│   ├── 09-current-state.md    # 当前：现状速览（结论 + 链接，不重复状态）
│   └── _archive/              # 01–10 原文归档（只加状态头，不改写）；check_docs 跳过该目录
├── references/
│   ├── contracts.md           # 铁律：domain/services/features 依赖方向；不 import 运行时分层
│   ├── verification.md        # 单测/真机/延迟/构建矩阵 + 已知坑（Gradle/JDK/NDK）
│   └── workflow.md            # L0/L1/L2、红队范围、阻塞上报
├── harness/
│   ├── config.json            # 路径/命令/预算/claims/adapters（唯一配置源）
│   ├── plans/                 # 唯一 active 计划 + _template
│   ├── evidence/              # schema/TEMPLATE/摘要 JSON
│   └── test-baseline.json     # unit.floor=65、expectedSkipped=0（只增不减）
├── scripts/
│   ├── gradlew-local.sh       # 由根目录 gradlew.local.sh 迁入（机器相关 shim）
│   └── verify-unit.sh         # 跑 testDebugUnitTest + 解析 JUnit XML → evidence 草稿
├── tools/                     # kit 生成：check_docs/check_agents/check_plan/evidence/verify_claim/token_estimate
│   ├── evidence_from_junit.py # v0.2.2 起由 kit 提供（JUnit XML → evidence 草稿，跨语言）
│   ├── check_hygiene.py       # v0.3.0 起由 kit 提供；过渡期宿主脚本（跟踪产物/符号链接/根白名单/大文件）
│   ├── check_layers.py        # 宿主：Android 分层 import 守卫
│   └── check_docmap.py        # v0.3.0 起由 kit 提供（改代码→必须动映射文档）
└── .github/workflows/verify.yml  # 静态门禁（kit CI adapter，python/make 即可）
```


### 2.4 文档蒸馏与重构（解决 A/C 的核心）

**两层模型**：

- `docs/` = **当前真源**（重写/提炼，必须与代码一致，索引在 `docs/README.md`）。
- `docs/_archive/` = **过程档案**（原文归档，只加日期与状态头，不改写正文；不被 AGENTS/README 当事实引用）。

> 为什么用 `_archive` 这个名字：贴合 kit 现成口径——`check_docs` 扫描 `docs/**/*.md` 时跳过 `runs/` 与 `_archive/` 目录，历史原文里的失效链接不会让当前门禁变红；`docs/README.md` 仍可用真实链接列出归档文件，保持可追溯。

**蒸馏映射**（01–08 是核心资产，不是垃圾）：

| 原文档 | 当前文档（重写/提炼） | 历史档案（保留原文） |
| --- | --- | --- |
| `01-product-prototype.md` | `docs/01-product.md`：产品规则/任务语义（校验后保留） | `_archive/01-product-design-2026-09.md` |
| `02-architecture.md` | `docs/02-architecture.md`：按代码重写实际分层/模块注册/并发/存储/线程 | `_archive/02-architecture-design-2026-09.md` |
| `03-tech-choices.md` | `docs/03-decisions.md`：**唯一决策表 D1..Dn**（听写/翻译/音频/语言能力/总结/存储/最低系统/架构套件；列选择、放弃项、理由、状态、证据链接） | `_archive/03-tech-choices-design-2026-09.md`（ML Kit 推演全过程） |
| `04-implementation-principles.md` | `docs/04-runtime.md`：流水线、UtteranceAssembler、路由、翻译节流、TTS、持久化、模型准备 | `_archive/04-implementation-design-2026-09.md` |
| `05-obstacles.md` | 仍成立的约束/阻塞 → `docs/03-decisions.md` 的"约束/风险"行 + `docs/05-known-issues.md` | `_archive/05-obstacles-2026-09.md` |
| `06-compromises.md` | 当前取舍 → `docs/05-known-issues.md`（已知妥协/限制） | `_archive/06-compromises-2026-09.md` |
| `07-roadmap.md` | `docs/06-roadmap.md`：Now/Next/Later + 链接 active 计划 | `_archive/07-roadmap-2026-09.md`（旧甘特与过程） |
| `08-on-device-llm.md` | `docs/07-on-device-llm.md`：核心技术资产，逐条对照代码校正（Tensor/KV/大核/实测） | 若数字重测：`_archive/08-on-device-llm-2026-09.md`，当前文档标"数字日期/设备" |
| `09-current-state.md` | 拆分：偏差 → 决策表；现状/进度 → active 计划 + 证据；`docs/09-current-state.md` 只留"现状速览 + 链接" | `_archive/09-current-state-2026-11.md`（过程快照） |
| `10-latency-optimization.md` | `docs/08-latency.md`：核心资产保留（归因、实测数字标日期/设备、方案与状态表） | `_archive/10-latency-2026-11.md` |

**规则**：

1. 当前文档首行：`> 状态：当前（2026-11-09）｜真源：<范围>`；历史档案首行：`> 状态：历史（写于 2026-09，勿作现状引用）｜当前对应：docs/xx`。
2. `docs/README.md` 是唯一索引：**当前文档 + 历史档案两张表**；新增/移动必须登记，`check_docs` 强制。
3. 决策与结论只写一处：`docs/03-decisions.md`（D-ID）；其他文档引用 ID，不重复结论。
4. 历史档案**不修改正文**；结论变化时更新当前文档，并在历史档案头加"YYYY-MM-DD 订正：见 docs/xx"。
5. 过程（05/06/07、commit 历史、旧 review）不删除——它们的价值是"当时为什么这么想"，但不再承担"现在是什么样"。
6. 环境事实出库：`/local`、设备名等本机事实移入 `scripts/gradlew-local.sh` 默认值 + `AGENTS.local.md`（gitignore）；仓库内只写通用路径。`sensitivePatterns` 增加 `"/local/"`（kit 内置只扫 `/local/`、`sk-`）。
7. `third_party/llama.cpp` 去符号链接：固定 tag + `FetchContent`/submodule + 校验，CONTRIBUTING 写"换机如何复现"。

**验收**：`docs/README` 覆盖 100%；抽查 3 处"当前文档 vs 代码"（引擎名/类名/阶段）0 冲突；历史档案 0 处被 AGENTS/README 当唯一真源；`grep '/local/' docs/` 0 命中。


### 2.5 状态层与过程文件治理（解决 B 的核心）

1. **唯一 active 计划**：`harness/plans/<date>-<topic>.md`，front matter 必填 scope/acceptance/verify；`check_plan` 校验"同一时间 1 个 active、必填节、越界改动声明"；完成改 `done` 并归档。
2. **证据链**：`scripts/verify-unit.sh` 跑真实单测 → 解析 `app/build/test-results/.../*.xml` 的 `tests/failures/errors/skipped` → 生成证据草稿 → `tools/evidence.py write`（要求 clean tree，绑定 commit）→ `verify-claim` 三值判定。**无证据 ID 的"已验证"按未验证处理。**
3. **进度一屏**：`make resume`（或 kit 生成的 `python3 tools/check_plan.py brief`）输出 active 计划 + 未验证项 + 下一步；`make handoff` 固化交接。README/09/10 的状态段改为"引用计划+证据"，不再各写一份。
4. **卫生传感器 `tools/check_hygiene.py`**（kit 目前不覆盖；本提案把它泛化进 v0.3.0，见附录 C·C4；Android 首版可先用宿主脚本落地）：
   - 禁止被跟踪的构建产物（`app/build/**`、`app/.cxx/**`、`*.apk`、`*.aab`、`*.log`）；
   - 禁止绝对符号链接（`git ls-files -s | mode 120000 且 target 以 / 开头`）；
   - 根目录文件白名单（`README/AGENTS/HARNESS/CONTRIBUTING/Makefile/gradlew*` 等）；
   - 禁止本机路径（`/local/`、`/local/`）；
   - 禁止 >5 MB 的跟踪文件。
   `make check-host` 接入 pre-push 与 CI；负向测试见 §2.8。
5. **一次清洁批次（Phase 3）**：删死代码（4 常量/`debounceJobs`/`translationPackBody`/`indeterminate` 分支）、debug Activity 移 debug source set 或 `exported="false"`、`prototype/platform.html` 移 `docs/_archive/prototype/`、`gradlew.local.sh` 移 `scripts/`、`.gitignore` 补 `.kotlin/`、`*.hprof`、`captures/`；桩代码做"实现/撤 UI/保留但标 UNVERIFIED"决策清单进计划。

### 2.6 代码质量传感器（kit 明确不覆盖，必须补）

| 传感器 | 命令/配置 | 拦截什么 |
| --- | --- | --- |
| ktlint（或 detekt 自带格式规则） | `./gradlew ktlintCheck`（或 detekt format） | 格式漂移、import 顺序 |
| detekt | `./gradlew detekt` + `detekt.yml`（ComplexMethod/TooManyFunctions/LongMethod/DuplicateCode/UnusedPrivateMember/MagicNumber 白名单） | 复杂度、重复、死代码、上帝类（现在 `ConversationViewModel` 786 行、`InterpretationViewModel` 754 行） |
| Android Lint | `./gradlew lintDebug`（baseline 可先接） | `exported`、未使用资源、API 兼容、Compose 规则 |
| 分层守卫 `tools/check_layers.py` | 纯文本扫描 import | `features/**` 不得 import `services` 实现/`Room`、`domain/**` 不得 import `android.*`、`services` 不得 import `features` —— 与 kit 的 `references/contracts.md` 对应 |
| 测试基线 | `harness/test-baseline.json`：`unit.floor=65` | 删测试/减用例（"测试只增不减"） |
| 死代码/桩清单 | 计划条目 + detekt + 人工复查 | 桩代码长期占位 |

> 这些是 **host 传感器**：写进 `Makefile` 的 `check-host` 与 CI，不修改 kit core。`verify-claim` 里加 `lint-pass`（type=static，command=`make check-host`），失败即 FAIL。

### 2.7 文档过期问题的额外机制（部分将进 kit v0.3.0）

- **`harness/docmap.json` 变更映射**（泛化进 kit 的 C5）：`{ "app/src/main/java/com/duiyi/android/services/translation/**": ["docs/03-decisions.md","docs/09-current-state.md"] }`；`tools/check_docmap.py` 在 pre-push/CI 里取"相对于上一个 claim/计划起点的 diff"，若命中映射但对应文档未改，则 exit 1（可配 waiver 注释）。
- **计划 DoD 增加"文档影响"节**：关闭计划前必须回答"本次改动更新了哪些当前文档/决策行；哪些历史文档无需动"。
- **收尾审计**：每月/大改后跑一次 docs 巡检（kit strict 的 scorecard/reviews 可承载；Android 可先手工）。
- 诚实边界：以上是**启发式**，能抓住"改了翻译链路却没动 03/09"这类高频漂移，抓不住"数字变了但文档里的 2.7s 没变"；后者只能靠冷启动首访与人工 review（见 §5）。

### 2.8 验收方式：负向注入（证明机制真的能拦）

接入不能只看"make check 绿"——要故意制造问题，确认变红：

| 注入 | 机制 | 预期 |
| --- | --- | --- |
| 删 `docs/README.md` 一行登记 / 加一个未登记 `docs/11-*.md` | `check_docs` 索引 | `make check` exit 1 |
| 改一个相对链接指向不存在文件（如把 `docs/01:10` 的坏链当靶子） | `check_docs` 链接 | exit 1 |
| 加一个未闭合代码围栏 | `check_docs` fence | exit 1 |
| 根目录新增 `NOTES.md` | `check_docs` rootMarkdownAllowed | exit 1 |
| 在 `AGENTS.md` 写 `/local/...` | `check_agents` sensitivePatterns | exit 1 |
| 制造 2 个 active 计划 / 计划缺 acceptance | `check_plan` | exit 1 |
| 脏树下写证据 | `evidence.py write` 拒绝 | exit 1 |
| 跟踪 `app/build/foo`、加绝对符号链接、根目录放 `scratch.log` | `check_hygiene`（宿主；v0.3.0 进 kit） | exit 1 |
| `features` 里 import Room 实现 | `check_layers`（宿主） | exit 1 |
| 删一个测试 | `unit.floor` | `verify-claim` FAIL |
| 改了映射代码路径但不动文档 | `check_docmap`（v0.3.0 kit） | exit 1 |

全部通过后，才能对用户说"接入完成"；这套注入也直接回答"改造后这些问题还在不在"——**同类问题下一次出现时，会在 push/CI 上被拦，而不是靠人发现**。

---

## 3. 逐条回答："改造后是否还存在这些问题"

### 3.1 文档混乱 → **结构性消除，内容性需一次重构**

- **会被机器拦住的**：无索引、断链、未闭合围栏、根目录 md 泛滥、公开文档超量、指令文件超预算/敏感串漂移。
- **不会被自动拦的**：两篇都登记但内容重复、同一事实写三处、标题结构混乱。这些靠 `docs/AGENTS.md` 的"单一真源"规则 + §2.4 的蒸馏重构（当前文档重写、历史原文归档、结论收敛到决策表）+ 冷启动首访检查。
- **残留等级：低**。做完 §2.4 后，"文档混乱"会变成"文档架构问题"，而不是"找不到/信不过"。

### 3.2 进度不直观 / 过程文件不清理 / 无用文件 → **大幅改善，但清理不是自动的**

- **会被机制强制的**：同一时间只有一个 active 计划、计划必填"进度/验证证据/未验证项/下一步"、完成必须证据、（证据/计划）每次提交都留下可追溯记录；`check_hygiene` 拦住新增的产物/符号链接/杂项根文件；pre-push/CI 让"顺手提交垃圾"直接失败。
- **不会被自动清理的**：已经存在的垃圾（如 `prototype/`、旧 debug Activity 导出、`gradlew.local.sh` 位置）需要 Phase 3 一次清理；"这个文件还有没有用"是判断问题，门禁只认白名单/黑名单。
- **残留等级：中低**。关键变化是**进度从"散落文档"变成"计划+证据一屏可读"**，且每次改动都被迫交代"未验证项/下一步"。

### 3.3 文档不及时更新（方案变了文档没更新） → **部分解决，别期待归零**

- **会被强制的**：文档有状态字段（当前/历史）+ 唯一索引 → "过期但假装当前"很难长期存在；决策表唯一 ID → 选型变更必须改一行状态，不再出现双轨；计划 DoD 要求写"文档影响"；v0.3.0 的 docmap 门禁拦住"改了代码没动映射文档"。
- **不会被自动判定的**：语义正确性（数字、结论、截图、命令、架构描述是否仍准确）。kit 没有也不可能有通用"文档语义一致性"传感器；`check_docs` 只做结构检查。
- **残留等级：中**。如果 `docmap` + 收尾审计 + 冷启动首访三件都做，可降到中低；只装 kit 不补这三件，会回到"过期后补横幅"的老路——**这是本方案最需要你确认投入的部分**。

### 3.4 代码不简洁 / 无用文件（代码层） → **kit 不管，必须另装传感器**

- kit 官方边界：不跑宿主测试、不解析业务输出、不管代码风格；`scope.allow/deny` 只约束"计划允许改哪里"，不评价"写得好不好"。
- 因此：**只接 kit = 这一项基本不变**。要解决必须加 §2.6 的 detekt/ktlint/lint/分层守卫/测试基线；即使加了，复杂度阈值与架构审美仍需 review。
- **残留等级：kit 单独=高；kit+传感器+一次清理=中低**。

### 3.5 其他问题（超出你列的清单）

| 问题 | 接入后的状态 | 说明 |
| --- | --- | --- |
| 环境不可复现（绝对符号链接、`/local/` 路径、本机 JDK shim） | **新增强制拦截**；存量需 Phase 3 清理 | `sensitivePatterns` + hygiene + CONTRIBUTING 复现步骤；llama.cpp 固定 tag/hash |
| 过程记录与 Git 历史不一致（`1c3bcce` 声称移除 .cxx 但只改 .gitignore） | **可被"证据/计划必须与提交对应"约束**，但无法自动回查历史谎报 | 以后所有"已完成"必须带 evidence id + commit；写计划时用 `git show` 复核 |
| 桩功能被当完成（总结/音频/语言能力） | **三值证据会把它变成显式 UNVERIFIED**；不能自动补实现 | 计划里列"实现/撤 UI/保留但标未验证"三选一 |
| 测试面窄（无 UI/instrumented、延迟手工） | **部分**：kit 只做静态；单测证据+基线可防删测试，真机仍需人工 | `references/verification.md` 写清"哪些必须真机、怎么记 UNVERIFIED" |
| 无 CI / 无静态分析 | **静态 CI 一条命令搞定**；unit CI 受 native 构建约束 | 首版 CI 只接静态；unit 证据本地生成（kit 设计如此） |
| 双语言构建（Kotlin+C++）验证矩阵 | **需在 verification.md 分层** | JVM 单测 / native 构建 / 真机 分开记；CI 不假装覆盖全矩阵 |

---

## 4. 实施计划（确认后执行）

### Stage A · kit v0.2.2（在 kit 仓，1.5–2 会话）

| Phase | 内容 | 验收 |
| --- | --- | --- |
| **A1 存量接入能力** | 新增 `scripts/harness-adopt`：只读盘点（文档/根目录/被跟踪产物/绝对符号链接/既有 Makefile/CI/测试命令）+ 输出改造报告 + docs 索引草稿 + 改造计划草稿；messy fixture 仓测试 | fixture 报告能列出断链、未登记文档、被跟踪产物；默认 0 写入；`--write-plan` 才落盘 |
| **A2 Android 生态** | `--language android` 探测（`settings.gradle*`/`build.gradle*`）+ 建议 `./gradlew testDebugUnitTest`；语言矩阵/README/SPEC 更新 | detect 单测；矩阵新增 Android 行；`--language` enum 更新 |
| **A3 JUnit 适配器** | `core/tools/evidence_from_junit.py`：多 JUnit XML → `{passed,failed,skipped,...}` 证据草稿（标准库） | 多 suite/失败/skip fixture；生成的 JSON 能被 `evidence.py write --from-json` 接受 |
| **A4 brownfield playbook** | `docs/playbook.md` 增"存量项目七步法"（盘点→基线→scaffold→文档蒸馏→清洁→传感器→负向注入/首访）+ 改造计划模板 | 文档评审通过；命令与 A1 一致 |
| **A5 发版** | `VERSION 0.2.2` + CHANGELOG/SPEC 更新；`make kit-check`（69 个既有 + 新增全绿）、kit 卫生扫描 0 命中；`make kit-publish` 同步独立仓 + tag `v0.2.2` + CI success；Android 只读试点报告存档 | 镜像仓 tag/CI；Android 仓 0 改动 |
| **合计** | | **1.5–2 会话** |

### Stage B · Android 仓改造（3.5–4 会话）

| Phase | 内容 | 产出 | 验收 | 估算 |
| --- | --- | --- | --- | --- |
| **P0 评估**（已完成） | 现状盘点、基线单测、方案、残留风险、kit 泛化提案 | 本文件 | 数据可复核 | 已做 |
| **P1 接入 scaffold**（0.5） | clone kit v0.2.2 → `harness-adopt` 报告审阅 → dry-run → init standard `--language android` → 调 `harness/config.json`（budgets/claims/publicBudget 16/sensitivePatterns）→ 首次 `make check` → 提交 scaffold | `AGENTS/HARNESS/CONTRIBUTING/docs/README/references/harness/tools/Makefile/.github` | `make check` exit 0；首次 commit；`git status` 干净 | 0.5 |
| **P2 文档蒸馏**（1.5–2） | §2.4：当前文档重写 + `_archive` 归档 + `docs/README` 双表 + `03-decisions.md`；README 瘦身；references 三篇；AGENTS/nested 规则；环境事实出库 | 文档树 | `make check` 0；跟踪文件 0 个 `/local/`；抽查 3 处当前文档 vs 代码 0 冲突；冷启动 5 问 ≥4 可答 | 1.5–2 |
| **P3 清洁批次**（0.5–1） | 死代码删除；桩代码决策清单；debug Activity 隔离；llama.cpp 去符号链接；`gradlew.local.sh` 迁移；`prototype` 归档；`.gitignore` 补全 | 干净仓 | `make verify-static` 0；单测 65 仍全绿；`check_hygiene` 0 | 0.5–1 |
| **P4 传感器与证据链**（1） | `scripts/verify-unit.sh`（调 kit JUnit 适配器）+ `lint-pass` claim；detekt/ktlint/lint 接线；`check_layers`/`check_hygiene`/（可选 `check_docmap`）；pre-push + CI | 门禁闭环 | 负向注入矩阵全红→恢复全绿；`verify-claim` 全 PASS；CI success | 1 |
| **P5 验收与回写**（0.5） | 负向注入全过；冷启动首访（非作者 agent）；计划归档演练；Android 卡点回写 kit（v0.2.3 issue/建议） | 验收记录 | 首访 5 问；`make check`/`verify-static`/`verify-claim` 全绿 | 0.5 |
| **合计** | | | | **3.5–4 会话** |

**总工作量**：Stage A 1.5–2 + Stage B 3.5–4 ≈ **5–6 会话**（比"直接接 v0.2.1"多约 1–1.5 会话，换来 kit 真实支持 Android + brownfield 能力，且 Android 仓只做一次接入）。

**回滚**：Stage A 在 kit 仓每 Phase 一个 commit，未发布可回退；Stage B 每 Phase 一个 commit；kit 产物无运行时依赖，最坏 `git revert` + 删除新增目录；`init` 冲突默认 fail 不覆盖，`--force` 先备份到 `.harness-init-backup/`。

**验收总判据（完成定义）**
1. `make check`、`make verify-static`、`make verify-claim --all` 全 exit 0；CI static success。
2. 干净 clone 后 `make check` 可跑（只依赖 python3/make/git）；单测证据绑定 commit、`git.dirty=false`。
3. `docs/README.md` 覆盖 100% 文档；0 断链；跟踪文件 0 个 `/local/`、0 个绝对符号链接、0 个构建产物。
4. 负向注入矩阵（§2.8）全部被拦，恢复后全绿。
5. 冷启动首访：给另一 agent/人 repo URL，5 问（现状/下一步/未验证/命令/规则）≥4 可答。
6. 计划归档演练一次：`done` 计划带 `submitted`/证据 ID，`check_plan` PASS。
7. kit 侧：v0.2.2 tag 发布、镜像 CI success、语言矩阵含 Android、kit 卫生扫描 0 命中。


---

## 5. 风险与未验证

| 风险 | 影响 | 对策 |
| --- | --- | --- |
| kit 对 Android/Gradle 未实测（现有 `language other` 兜底） | init/命令推断可能不合预期 | 先 `harness-adopt` 只读盘点 + `--dry-run`；`--test-command` 显式；v0.2.2 增加 `android` 探测与测试 |
| **Stage A 延期，拖慢 Android 落地** | Android 仓验收推迟 | A1–A4 可分批评审，先发 v0.2.2-rc？→ 不引入 rc，改为"v0.2.2 范围锁死 4 项、其余进 v0.3.0"；P2 文档蒸馏可与 Stage A 并行（不依赖 kit） |
| **kit v0.2.2 新工具引入回归** | 破坏既有 profile 用户 | 新能力独立文件 + 默认配置缺省不启用；69 个既有测试必须全绿；kit 卫生扫描（无 Duiyi 词）；镜像发布后 Android 作为首个升级试点 |
| 蒸馏判断失误 | 丢掉设计理由/历史细节 | 历史原文**全量**归档不改写；当前文档只提炼结论；`03-decisions.md` 每条标"来源 `_archive/xx@date`"可回溯 |
| detekt/ktlint 首次接入噪音大 | 门禁长期红/被跳过 | 先 `detekt --baseline`，再逐批还债；CI 允许 warning 阈值 |
| CI 跑 unit 成本高（NDK/CMake） | CI 只静态，动态覆盖缺口 | 首版 CI 静态；unit 证据本地（与 kit 设计一致）；再决定是否加自托管/缓存 |
| 真机验证仍人工（荣耀机分叉、延迟探针） | 无法 CI 自动判绿 | verification.md 分层；未跑写 UNVERIFIED + 手动步骤（三值证据允许） |
| 文档语义过期无法自动判 | 旧数字/结论仍可能残留 | docmap + DoD + 收尾审计 + 冷启动首访；接受"降低"而非"归零" |
| 跨仓一致性（iOS/Android 对译） | 两端文档/规则漂移 | 各自独立 harness；共享事实只引用（不复制）；跨仓同步靠人 |
| 改动业务代码的连锁风险（P3 删死代码/桩） | 编译/行为回归 | 65 单测 + 真机手测清单；桩代码只做决策不顺手实现 |

**未验证（本评估内）**：设备/真机能力（本机无 Android 设备环境信息）、CI 首次运行、detekt 在本仓的真实噪音、`testDebugUnitTest` 在全新 clone（无 NDK）下的行为、kit 在 Gradle 仓上的 init 输出。

---

## 6. 需要你确认的决策

| # | 决策 | 建议默认 |
| --- | --- | --- |
| 1 | 推进顺序：**Stage A（kit v0.2.2）→ Stage B（Android 接入）** / 直接接 v0.2.1 后再升级 | **Stage A → B**（Android 只做一次接入；kit 升级路径用真实项目试点） |
| 2 | kit v0.2.2 范围：C1 adopt + C2 android + C3 JUnit + C4 playbook（+ C8 模板）/ 缩小到只 android 支持 / 全量（含 v0.3.0 传感器） | **上述 4 项 + C8**（1.5–2 会话）；v0.3.0 传感器单独排期 |
| 3 | profile：standard / minimal / strict | **standard**（发布前可再升 strict） |
| 4 | 文档策略：**蒸馏**（当前文档重写 + history 原文归档） / 只加历史横幅 / 原地改写 | **蒸馏**（按 §2.4 映射；历史原文不删不改） |
| 5 | P3 是否动代码（删死代码/改 manifest/迁脚本/llama.cpp 去符号链接） | 同意（每项单独 commit，65 单测护航） |
| 6 | 代码质量传感器：detekt+ktlint+lint+分层守卫 / 先只 lint / 暂不 | **detekt+ktlint+lint+分层守卫**（kit 管不到，不补等于没解决"代码不简洁"） |
| 7 | docmap / hygiene / statusPolicy：随 v0.3.0 做 / 先宿主脚本 / 暂不做 | **随 v0.3.0 进 kit**；Android 首版可先宿主脚本兜底 |
| 8 | CI 范围：只静态 / 静态+unit（需评估 native 成本） | 首版**只静态**，unit 后评估 |
| 9 | kit 发版后是否同步回 iOS 仓 `harness-kit/` | 是（`make kit-publish` + 本仓同步一次；iOS 作为 kit 维护源） |


---

## 附录 A · 本次取证命令与结果

```bash
# 仓库/跟踪/历史
git -C realtimeTranslatorAndroid status --porcelain        # 空（跟踪文件干净）
git ls-files | wc -l                                        # 115
git log --oneline                                           # 3 commits
git ls-files -s third_party/llama.cpp                       # 120000 ... 0  third_party/llama.cpp
git ls-tree -r 440294c --name-only | grep -c cxx            # 0（初版无 .cxx）
git show 1c3bcce --stat                                     # 仅 .gitignore，1 file changed

# 单测基线（2026-11-09）
./gradlew.local.sh testDebugUnitTest --console=plain        # BUILD SUCCESSFUL in 49s, exit 0
# JUnit XML: tests=65 failures=0 errors=0 skipped=0（16 classes / 13 test files）

# 文档
find docs -name '*.md' | wc -l                              # 10（无 docs/README.md）
wc -l docs/*.md README.md | tail -1                         # 2351 行
python3 token_estimate.py（kit）                             # 36,645 tokens
grep -rn 'ML Kit|SpeechRecognizer|Gemini Nano' docs/0[2-8]*.md | wc -l   # 61
grep -rln '/local/' --include='*.md' --include='*.sh' .   # README.md / docs/09 / gradlew.local.sh
相对链接检查（脚本）：1 条断链 docs/01-product-prototype.md:10 -> ../../../realtimeTranslatorOptimize/docs/09-platform-prototype.md

# 死代码
grep -rn 'FIRST_TRANSLATION_MS|TRANSLATION_MS|VOICE_FIRST_MS|VOICE_NEXT_MS' app/src   # 仅定义
grep -n 'debounceJobs\[' InterpretationViewModel.kt          # 无新增点（只 remove/clear）
grep -rn 'translationPackBody' app/src                       # 仅定义
grep -rn 'indeterminate = true' app/src                      # 仅测试

# 卫生
du -sh app/.cxx app/build                                    # 1.4G / 903M
find app/.cxx -type f | wc -l                                # 644
grep -n 'exported' app/src/main/AndroidManifest.xml          # 34/39 debug Activities exported=true
```

## 附录 B · 建议的 `harness/config.json` 关键值

```json
{
  "kitVersion": "0.2.1",
  "project": { "name": "对译 Duiyi Android", "language": "other" },
  "paths": { "rootDocs": ["AGENTS.md"] },
  "instructions": {
    "budgets": {
      "AGENTS.md": 1200,
      "references/contracts.md": 700,
      "references/verification.md": 700,
      "references/workflow.md": 700
    },
    "sensitivePatterns": ["/local/", "/local/", "sk-"]
  },
  "docs": {
    "publicWhitelist": [
      "README.md", "AGENTS.md", "docs/README.md", "docs/AGENTS.md",
      "docs/01-product.md", "docs/02-architecture.md", "docs/03-decisions.md",
      "docs/04-runtime.md", "docs/05-known-issues.md", "docs/06-roadmap.md",
      "docs/07-on-device-llm.md", "docs/08-latency.md", "docs/09-current-state.md"
    ],
    "publicBudget": 16,
    "rootMarkdownAllowed": ["README.md", "AGENTS.md", "HARNESS.md", "CONTRIBUTING.md", "CLAUDE.md"]
  },
  "commands": {
    "check": "make check",
    "verify": "make verify-static",
    "test": "./scripts/verify-unit.sh"
  },
  "claims": [
    { "name": "unit-tests-pass", "type": "test-count", "baseline": "harness/test-baseline.json", "floor": "unit.floor", "expectedSkipped": "unit.expectedSkipped", "command": "./scripts/verify-unit.sh" },
    { "name": "static-pass", "type": "static", "command": "make check" },
    { "name": "lint-pass", "type": "static", "command": "make check-host" }
  ]
}
```

`harness/test-baseline.json`：`{ "unit": { "floor": 65, "expectedSkipped": 0 } }`（后续只增不减）。

## 附录 C · 泛化进 kit：从 Android 改造场景提炼的能力（v0.2.2 / v0.3.0）

**泛化原则**（避免 kit 变成"每个项目一套"）：

1. 进 `core/` 的条件：**语言无关 + 配置驱动 + 有单测 + 不引入第三方依赖**；任一条不满足，就放 `adapters/`、`docs/` 或宿主仓库。
2. 所有新能力默认**缺省不启用**（config 不写就跳过），保证既有 69 个测试与三档 profile 的"空白项目一次通过"不回归。
3. 每个新能力配 fixture 负向测试；kit 卫生扫描（无 `Duiyi|duiyi|对译|...`）必须仍为 0 命中。
4. 版本节奏：**v0.2.2 = 接入能力**（本次 Android 落地必需）；**v0.3.0 = 传感器能力**（通用但改动大，单独排期）。

### C1 `scripts/harness-adopt`：存量项目盘点/接入向导（v0.2.2，最高价值）

- **泛化自**：本次 Android 盘点（手工跑了 20+ 条只读命令才敢下结论）；kit 现在只有"空白项目 init"，没有"存量项目怎么接"。
- **行为**：`harness-adopt --target . [--report PATH] [--write-plan]`，默认 **0 写入**：
  - 仓库/语言/构建探测（含 Gradle/Android、Xcode、Node、Python、Go）；
  - 文档盘点：`docs/**` 数量、根 md、未索引文档、断链、围栏、疑似过期标记（"写于实现之前/过时/待验证"关键词）；
  - 卫生盘点：被跟踪构建产物、绝对符号链接、本机路径、大文件、根目录杂项；
  - 既有门禁盘点：Makefile/CI/Makefile.harness 冲突预判；
  - 输出：Markdown 报告 + `docs/README.md` 索引**草稿**（不落盘）+ 改造计划草稿（`--write-plan` 时写到 `harness/plans/`，需先有 scaffold）。
- **测试**：fixture 仓（脏文档 + 被跟踪产物 + 符号链接 + 既有 Makefile）→ 报告包含全部问题；默认 0 写入；`--write-plan` 仅写计划文件。
- **验收**：对 Android 仓只读跑出本文件 §1 的核心数据（断链 1、过期标记 61、`.cxx` 历史不一致可提示、绝对符号链接 1）。

### C2 `--language android` 探测与建议命令（v0.2.2）

- **泛化自**：kit `detect_language` 不认 Gradle → 只能 `other` 兜底。
- **行为**：`settings.gradle*`/`build.gradle*`（含 `.kts`）→ `android`；建议命令 `./gradlew testDebugUnitTest`（并打印说明：JDK 17–21、wrapper 版本由项目固定；kit 不代跑、不解析输出）；SPEC §8/README 语言矩阵/help 同步更新。
- **测试**：`detect_language` 单测 + `test_test_command_inference` 覆盖 android；语言矩阵文档断言。
- **验收**：`--language android` init 后 `commands.test` 正确；README 矩阵新增 Android 行。

### C3 `core/tools/evidence_from_junit.py`：JUnit XML → 证据草稿（v0.2.2）

- **泛化自**：Android/Gradle 的 JUnit XML；同格式被 Maven/Surefire、pytest（junitxml）、Go 的 `go-junit-report` 等使用，**跨语言**。
- **行为**：`evidence_from_junit.py --xml GLOB... [--command CMD] [--environment k=v ...] [--out FILE]` → 输出可直接 `evidence.py write --from-json` 的草稿（`result.passed/failed/skipped/durationSec`），聚合多 suite；文件格式错误 exit 2。
- **测试**：单 suite / 多 suite / 失败 / skip / 空结果 fixture；与 `evidence.py` 串联集成测试。
- **验收**：Android 的 13 个测试文件 XML 能生成 `passed=65 failed=0 skipped=0` 且 `verify-claim` 接受。

### C4 `docs/playbook.md` 增"存量项目七步法"（v0.2.2）

- **泛化自**：本次从"混乱存量"到"门禁闭环"的实际推进顺序。
- **七步**：① 只读盘点（C1）→ ② 基线测试与证据 → ③ scaffold（init，不碰既有文档）→ ④ 文档蒸馏（当前/历史两层，见 §2.4）→ ⑤ 清洁批次（死代码/产物/环境事实）→ ⑥ 宿主传感器（分层/卫生/docmap）→ ⑦ 负向注入 + 冷启动首访验收。
- 每步给命令、退出信号、回滚点；附"存量项目常见坑"（双真源、历史文档误引用、构建缓存入库、环境路径泄漏）。
- **测试**：文档 lint（kit 已有 docs 门禁只查链接/预算）；人工评审。

### C5 `core/tools/check_docmap.py`：变更→文档映射门禁（v0.3.0）

- **泛化自**："改了翻译链路，03/09 文档没更新"这类高频漂移。
- **配置**：`docs.changeMap: { "<glob>": ["docs/xx.md", ...] }`；`check_docmap.py --base <git ref>` 对比改动路径，命中映射但对应文档未改 → exit 1；`--waiver` 允许计划里记录豁免。
- **放置**：`strict` profile 默认接入 `verify-static`；standard 可选 target。
- **风险**：误报（重构性改动）→ 先只覆盖"高价值路径"，并允许在计划/提交信息里显式豁免。

### C6 `core/tools/check_hygiene.py`：通用卫生门禁（v0.3.0）

- **泛化自**：被跟踪构建产物、绝对符号链接、根目录杂项、本机路径、大文件。
- **配置**（`hygiene`）：`trackedArtifacts: ["app/build/**", "*.apk"]`、`forbidAbsoluteSymlinks: true`、`rootAllowlist: [...]`、`maxTrackedFileBytes: 5242880`、`localPathPatterns`（复用 sensitivePatterns）。
- **放置**：standard 的 `check`（配置缺省则跳过）。
- **测试**：tmp git fixture 注入 5 类违规 → exit 1；正常仓 exit 0。

### C7 `check_docs` 增 `docs.statusPolicy`：文档状态规范（v0.3.0）

- **泛化自**：`01–08` 既像设计史又像现状、`09` 自称实况却漂移。
- **配置**：`docs.statusPolicy: { requiredFor: "docs/*.md", bannerRegex, statuses: ["current","historical","archive"], currentMustBeIndexed: true }`；historical 文档不得被根 `AGENTS.md` 当唯一真源引用（可配）。
- **放置**：minimal/standard（可选开关）。
- **限制**：只校验状态声明与索引关系，**不校验语义**（明确写进文档，避免误以为能自动防过期）。

### C8 brownfield 改造计划模板（v0.2.2，随 C1）

- `core/templates/harness/plans/_adoption.md.template`：盘点结论、当前/历史文档映射、清洁清单、传感器接线、负向注入验收、未验证项；`harness-adopt --write-plan` 用它生成草稿。

### C9 `scripts/harness-upgrade`：跨版本 scaffold 升级（v0.3.0，候选）

- **泛化自**：v0.2.1 → v0.2.2 的升级需要人工 dry-run 合并（playbook 自认未验证）。
- **行为**：`harness-upgrade --to <kit_root> [--dry-run]` 列出"新增/变更/冲突"文件并按 config 合并，冲突默认 fail；不改用户内容（AGENTS 等只提示差异）。
- **风险**：与 init 的 `--force` 语义重叠，先只做"diff 报告"最小版。

### C10 `scripts/harness-selftest`：门禁反向自测（v0.3.0）

- **泛化自**：本次 §2.8 的负向注入验收是手工做的；而门禁本身可能因为"预算调宽/白名单放大/配置写错"变成**空门禁**（看起来绿，其实什么都没拦）。这是 harness engineering 里最该有、也最容易被忽略的一层：**传感器也要被测试**。
- **行为**：`harness-selftest --target . [--kinds docs,plan,evidence,hygiene]`：
  1. 在临时目录复制目标仓（含 `.git`；或 `git worktree` 浅拷贝）；
  2. 逐项注入通用故障：断链、未登记 `docs/*.md`、未闭合围栏、根目录新增 md、两个 active 计划、计划缺 acceptance、脏 tree 写证据、被跟踪构建产物、绝对符号链接；
  3. 期望对应命令 exit≠0，全部符合则 exit 0，输出"注入 → 命中门禁"矩阵；
  4. 原仓 0 修改（失败也清理临时目录）。
- **放置**：strict 的 `make sensors-selftest`（默认不挂 pre-push，CI 可选）；kit 自身测试覆盖"注入必红 / 恢复必绿"。
- **风险**：大仓复制慢 → 只复制配置声明路径 + `.git`，或提供 `--max-bytes` 上限；不适用于没有 git 的目录。
- **验收**：在 Android 仓跑一次，自动复现 §2.8 矩阵；把"门禁是否真的在拦"变成可重复命令。

### 版本与验收

| 版本 | 范围 | kit 测试 | 前置 |
| --- | --- | --- | --- |
| **v0.2.2** | C1、C2、C3、C4、C8 | 69 → ≈85 | Android 只读试点 + 三档 profile 回归 |
| **v0.3.0** | C5、C6、C7、C9、C10（+ C1 增强） | ≈85 → ≈100 | v0.2.2 在 Android 仓真实接入后再定 |

**发布检查单**：`SPEC.md` §4/§8/§9 更新（新 CLI/新配置字段/新测试契约）→ `README` 语言矩阵与能力表 → `CHANGELOG` → `make kit-check` 全绿 → kit 卫生扫描 0 → `make kit-publish` 同步 <https://github.com/DavidTeam2008/harness-kit> + tag + CI → iOS 仓 `harness-kit/` 与镜像漂移检查（`make kit-drift`）。

**明确不做**（避免过度泛化）：Android 专用构建逻辑（NDK/CMake/JDK 版本探测）、代码质量工具封装（detekt/ktlint 由宿主配置）、真机/延迟验证（宿主 `references/verification.md`）、跨仓同步（人工）。

