# 验证矩阵与命令（唯一入口）

> 触发：跑检查、补测试、写证据或宣称「完成」前读。配置 [`../harness/config.json`](../harness/config.json)；流程 [`workflow.md`](workflow.md)。

## 1. 门禁分层

| 层 | 命令 | 判定 |
| --- | --- | --- |
| L0 静态 | `make check`（docs/agents/plan） | 秒级；改动后必跑 |
| 宿主静态 | `make check-host`（分层 + 卫生） | 只依赖 python3/git；CI 可跑 |
| standard | `make verify-static`（check + 证据 schema + check-host） | 完成前必跑 |
| 宿主质量 | `make check-quality`（detekt + ktlint + Android Lint） | 需 JDK 17–21/SDK；本机 |
| 证据三值 | `make verify-claim` | PASS/FAIL/UNVERIFIED；无证据 = UNVERIFIED |

## 2. 变更类型 → 最低验证

- 文档/规则：`make check`。domain/ViewModel：`./scripts/verify-unit.sh`。services/引擎/持久化：真机手工。构建/配置/CI：`make verify-static` + 干净环境复跑。发布：verify-static + verify-claim + 回滚。

## 3. JVM 单测与证据

- 跑测：`./scripts/verify-unit.sh`（`--rerun-tasks` 强制重跑）；JUnit XML 在 `app/build/test-results/`；基线 65、skip 0（[`../harness/test-baseline.json`](../harness/test-baseline.json)）。
- 取证：`make evidence-test`（要求 clean tree）→ JUnit XML 聚合成 `tests-pass` 证据写入 `harness/evidence/`；提交证据后 `make verify-claim` PASS。
- 删测试会触发基线 FAIL；`passed` 为 testcase 聚合口径。

## 4. 质量基线

- `make check-quality`：detekt（复杂度/死代码/重复）、ktlint（格式）、Android Lint（`lintDebug`）。
- 三份 baseline（`app/detekt-baseline.xml`、`ktlint-baseline.xml`、`lint-baseline.xml`）记录存量债；新增问题失败。修完后可重生成（`detektBaseline` / `ktlintGenerateBaseline` / `updateLintBaseline`）。

## 5. 真机手工（荣耀 ALP-AN00 / Android 14）

- `./gradlew assembleDebug` → `adb install -r app/build/outputs/apk/debug/app-debug.apk`。
- 主路径：面对面/同传/会议/历史；延迟：`.debug.LatencyDebugActivity`，平放聊 8–10 轮，读 `latency-probe.txt` 中位数；自检：`.debug.TranslationSelfTestActivity`。口径见 [`../docs/08-latency.md`](../docs/08-latency.md)。

## 6. 不该跑的 / CI 边界

- 不用模拟器证性能；不借未信任设备；非 JDK 17–21 不硬跑单测。
- CI 只跑 `make verify-static`（含宿主静态）；质量/单测/真机在本机。

## 7. 已知坑

- JDK 17–21：AS JBR25 报 `25.0.2`；`scripts/gradlew-local.sh` 自动挑 17–21。
- Gradle 插件解析失败：先查 `~/.gradle/gradle.properties` 是否指向已停代理；可临时 `-Dhttp.proxyHost= -Dhttps.proxyHost= ...` 覆盖。
- `.cxx` 异常删缓存重建；模型权重 2.49GB 失败重试；真机亮屏解锁。

## 8. 未验证写法

- 写「未验证 + 手动步骤 + 原因」，不得写成通过；环境问题≠代码问题。
