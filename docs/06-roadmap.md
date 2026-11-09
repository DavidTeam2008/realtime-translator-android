# 06 路线图 · Android

> 状态：当前规范（Now / Next / Later）。**进度权威 = active 计划 + 证据**，不是本页：当前计划见 [`../harness/plans/2026-11-10-android-adoption.md`](../harness/plans/2026-11-10-android-adoption.md)。
> 本页只维护方向与顺序：不写日期承诺、不做甘特、不写百分比；已完成条目写「已完成（日期）」，未验证条目写「未验证」。
> 最后核对：2026-11-10。决策背景见 [`03-decisions.md`](03-decisions.md)，问题与桩清单见 [`05-known-issues.md`](05-known-issues.md)。

## Now（进行中：harness 改造 P2–P5）

当前 active 计划：`2026-11-10-android-adoption`（Stage B）。四个阶段的**验收口径以计划为准**，本页只列内容。

| 阶段 | 内容 | 完成判据（详见计划） |
| --- | --- | --- |
| P2 文档蒸馏 | 当前 / 历史两层分离；本文件组 `03-decisions` / `05-known-issues` / `06-roadmap` 重写；`docs/README.md` 索引 100%；01–08 原文归档 `_archive/` | 文档门禁 PASS、索引无缺、历史只留归档 |
| P3 清洁批次（已完成 2026-11-10） | D-6 分项已修：符号链接 → 固定 tag、debug 入口 → `src/debug`、死代码删除、`.gitignore` 补全、`gradlew.local.sh` → `scripts/gradlew-local.sh` | 跟踪文件 0 本机绝对路径（`check_hygiene` PASS）；65 单测 PASS |
| P4 传感器 | `check_hygiene` / `check_layers`、detekt + ktlint + Android Lint、JUnit XML → evidence → `verify_claim`、pre-push/CI | `make check-host` 0；`tests-pass` 证据 PASS |
| P5 验收 | 负向注入矩阵、冷启动首访 ≥4/5、计划 done/归档演练 | 注入必红、恢复必绿；首访可答 |

**已完成（2026-11-10）**：P1 接入 harness-kit standard profile，`make check` / `make verify-static` PASS，65 个 JVM 单测为基线；P2 文档蒸馏（当前/历史两层、`_archive/`、决策表 D1–D15）；P3 清洁批次（符号链接/调试入口/死代码/本机路径/`.gitignore`，`check_hygiene` PASS）。

## Next（下一步，按优先级）

### N1 延迟（最高优先；先测量，再改）

- **先补测抢核**：并发听写时 partial 解码与生成共抢大核；用 `ComputeGate` 的「生成期间跳过 partial」开关做两轮 A/B，对比 `gen` 中位数。**数据出来前不调 VAD 静音窗与 `HOLD_NS`。**
- **流式回字幕**：生成 token 增量上屏，零质量风险，总耗时不变但「在干活」的体感明显。
- **增量分段翻译 A/B**：默认关；用长句对比「首句译文出现时间」与「可读性」，质量退化明显就保持关闭（详见 [`08-latency.md`](08-latency.md)）。
- **专用小模型分流评估**：Hy-MT2-1.8B（1.25-bit GGUF）/ small100（ONNX）先在同一组真实对话句子上测「延迟 + 可读性」；许可证与运行时已核（ONNX Runtime 已随包），**未做 A/B 前不改默认引擎**。
- **D-1 真机复验**：短句松口后 1.4 s 内出译文，`joiner_hold` 稳定在约 1400 ms。

### N2 可信度（桩三选一 + 能力探测）

- 总结 / 音频策略 / 语言能力 / 按语言对下载：按 [`05-known-issues.md`](05-known-issues.md) 第 2 节的三选一建议落地（实现 / 撤 UI / 标未验证），不允许长期「入口在、功能恒不可用」。
- `DeviceCapabilityProbe` 填真实能力（端侧语言列表 / `checkRecognitionSupport`），保留当前退化规则作兜底；泰 / 越与日语 / 韩语的灰置结果需真机核对。
- 会后总结：有 AICore 设备前维持「不谎称可打开」的文案；是否实现取决于设备覆盖评估。

### N3 工程（便宜但需要）

- D-3 模型完整性（期望字节 / 校验和）、D-4 Room 增量写、D-5 诊断日志轮转。
- CI 真实设备矩阵，替代纯人工真机清单；至少覆盖一台非荣耀机。
- P3 清洁后的真机手测清单复跑（听写 / 翻译 / TTS / 导出 / 恢复）。

## Later（更远，不排期）

- **非荣耀厂商验证**：Pixel 8/9、Android 14 三星、无端侧识别机的真机矩阵（当前只有荣耀一台验证过）。
- **按语言对 / 小模型分发管理**：只有在引入分流小模型之后才有意义（D14 演进）。
- **统一性能基线**：Release 真机、n≥10、同口径；把现有开发期自检数字升级为可复核证据（当前延迟结论见 [`08-latency.md`](08-latency.md)）。
- **长会与同传稳定性**：45 分钟连续运行、发热 / 降频、蓝牙 SCO 下读出与识别的互相影响。

## 已完成（只写已有事实与日期）

- **2026-09**：M1–M5 代码路径落地（引导、面对面、任务与 Room、同传读出、会议、导出）；总结为桩；延迟专项代码已写但未真机验证。
- **2026-11-10**：P1 接入 harness-kit standard profile（`make check` / `make verify-static` PASS，65 JVM 单测基线）；历史文档迁入 `_archive/`。

## 进度与证据约定

- 进度唯一权威：当前 active 计划 + `harness/` 证据（证据格式见 `harness/AGENTS.md` 与证据 schema）；计划完成后改 `done` 并归档。
- 本页条目开始 / 完成时：先改计划（进度、验收、证据），再回来更新本页条目；不要用本页代替计划。
- 不写日期承诺、甘特、百分比；「计划」不等于「已完成」；未验证结论写「未验证」。

## 风险与依赖

- 真机只有荣耀 ALP-AN00 一台（见 [`05-known-issues.md`](05-known-issues.md) 第 4 节）；非荣耀结论必须等设备。
- 性能数字口径未统一（单次自检 vs n≥10），引用必须注明来源与设备。
- 模型体积约 2.49 GB + 听写权重约 240 MB，首次准备约 18 s 级；网络只用于模型下载。
- harness 改造与产品工作并行时，同一时间只保留一个 active 计划，避免状态漂移。

相关：决策 [`03-decisions.md`](03-decisions.md) · 已知问题 [`05-known-issues.md`](05-known-issues.md) · 延迟 [`08-latency.md`](08-latency.md) · 现状 [`09-current-state.md`](09-current-state.md) · 文档索引 [`README.md`](README.md) · 历史档案 [`_archive/README.md`](_archive/README.md)。
