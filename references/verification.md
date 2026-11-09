# 验证矩阵与命令（唯一入口）

> 触发：跑检查、补测试、写证据或宣称「完成」前读。配置 [`../harness/config.json`](../harness/config.json)；流程 [`workflow.md`](workflow.md)。

## 1. 三层门禁

| 层 | 命令 | 判定 |
| --- | --- | --- |
| L0 静态 | `make check`（docs/agents/plan） | 秒级；改动后必跑 |
| standard | `make verify-static`（check + 证据 schema） | 完成前必跑 |
| 证据三值 | `make verify-claim` | PASS/FAIL/UNVERIFIED；无证据 = UNVERIFIED（exit 2） |

## 2. 变更类型 → 最低验证

- 文档/规则：`make check`。domain 与 ViewModel 逻辑：`./scripts/verify-unit.sh`。services/引擎/持久化：真机手工。构建/配置/CI：`make verify-static` + 干净环境复跑。发布：verify-static + verify-claim + 回滚步骤。

## 3. JVM 单测

- `./scripts/verify-unit.sh`（JUnit XML 在 `app/build/test-results/`；P4 后自动转证据）；基线 65、skip 0，门槛 [`../harness/test-baseline.json`](../harness/test-baseline.json)；重跑加 `--rerun-tasks`。

## 4. 真机手工（荣耀 ALP-AN00 / Android 14）

- 构建安装：`./gradlew assembleDebug`（JDK 17–21）+ `adb install -r app/build/outputs/apk/debug/app-debug.apk`。
- 主路径：面对面/同传/会议/历史；延迟用 `adb shell am start -n com.duiyi.android/.debug.LatencyDebugActivity`，平放聊 8–10 轮，`adb pull /data/data/com.duiyi.android/files/latency-probe.txt`，读中位数 speech_to_endpoint、final_decode/final_rtf、joiner_hold、gen；自检用 `.debug.TranslationSelfTestActivity` 看 prepare/prefix/suffix/gen ms。
- 口径与数字见 [`../docs/08-latency.md`](../docs/08-latency.md)；单次样本不算结论。

## 5. 不该跑的

- 不用模拟器证性能（native 与 SoC 差异大）；不借未信任设备（现场音频）；不在非 JDK 17–21 环境硬跑单测。

## 6. CI 边界

- `.github/workflows/verify.yml` 只跑静态（ubuntu）；JVM 单测在本机；native/NDK 与真机不进 CI。

## 7. 已知坑

- JDK 17–21 + Gradle 8.10.2 + AGP 8.7.2：AS 内置 JBR25 报 `25.0.2`，改用 17–21 的 JDK 或本地 shim。
- `.cxx` 缓存异常：删 `app/.cxx` 重建。模型权重（2.49GB）首次下载失败重试。真机需亮屏解锁。

## 8. 未验证写法

- 写「未验证 + 手动步骤 + 原因」，不得写成通过；环境问题≠代码问题。
