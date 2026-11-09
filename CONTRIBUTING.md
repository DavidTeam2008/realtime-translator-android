# CONTRIBUTING · 对译 Duiyi Android

> 目标：让新人和 AI Agent 在 30 分钟内能构建、能跑单测、能上真机、知道怎么算“完成”。
> 规则入口见 [`AGENTS.md`](AGENTS.md)，验证矩阵见 [`references/verification.md`](references/verification.md)，harness 地图见 [`HARNESS.md`](HARNESS.md)。

## 1. 环境要求

| 项 | 要求 |
| --- | --- |
| JDK | **17–21**（Gradle daemon 用；不要用 25） |
| Gradle | 工程自带 wrapper，固定 **8.10.2**，不要升级 |
| Android SDK | compile/target 35，minSdk 34，仅 `arm64-v8a` |
| NDK / CMake | 由 AGP 管理；llama.cpp 走 `app/src/main/cpp/CMakeLists.txt` |
| Android Studio | 可用，但内置 JBR 的 Gradle 版本/JDK 需按下方坑位处理 |

`local.properties` 写入本机 SDK 路径（`sdk.dir=...`），**不入库**。NDK 编译中间产物在 `app/.cxx/`，同样不入库。

## 2. Gradle / JDK 已知坑（Android Studio Quail 3 内置 JBR 25）

| 现象 | 真正原因 | 处置 |
| --- | --- | --- |
| `Plugin [id: 'com.android.application', version: '8.7.2'] was not found`（仓库都搜过） | Gradle 8.14.x 与 AGP 8.7.2 不兼容，不是插件缺失 | 用 wrapper 固定的 **Gradle 8.10.2** |
| `What went wrong: 25.0.2`（只有版本号） | Kotlin 2.0.21 的 `JavaVersion.parse` 解析不了 25 | Gradle 守护进程换 **JDK 17–21** |
| AS 提示升级 Gradle | 升级会落回上一条 | **不要接受**，除非同时升级 AGP/Kotlin |

命令行可用 `scripts/gradlew-local.sh`：它会从 `JAVA_HOME` / `~/.gradle/jdks` / 系统 JDK 里挑 17–21 再调 wrapper（仓库不保存机器路径）。AS 中设置 `Settings → Build Tools → Gradle → Gradle JDK` 为 17/21。

## 3. 首次构建

```bash
# 1) 配置本机 SDK（写入 local.properties，不入库）
#    sdk.dir=<你的 Android SDK 路径>
# 2) 构建 debug
./gradlew assembleDebug
# 3) 如命令行的默认 JDK 是 25，用仓库脚本挑 17–21
./scripts/gradlew-local.sh assembleDebug
```

## 4. 单测（JVM，无需真机）

```bash
./scripts/verify-unit.sh            # 推荐：JUnit XML 写到 app/build/test-results/testDebugUnitTest
./gradlew testDebugUnitTest         # 等价直连（JDK 17–21）
```

基线 65 个 JUnit4 用例，只增不减；`harness/test-baseline.json` 的 `unit.floor=65` 是门禁依据。

## 5. 真机

参考机：**荣耀 ALP-AN00（MagicOS 8.0 / Android 14）**。真机优先，模拟器不验证听写/翻译链路。

```bash
adb devices
./gradlew installDebug
adb shell am start -n com.duiyi.android/.app.MainActivity
```

诊断入口（debug 包）：

```bash
adb shell am start -n com.duiyi.android/.debug.LatencyDebugActivity
adb shell am start -n com.duiyi.android/.debug.TranslationSelfTestActivity
```

首次运行需走引导下载模型（SenseVoice ≈240 MB + TranslateGemma ≈2.49 GB），并授予麦克风权限。设备分屏/悬浮窗可能影响录音，测试前先退出分屏。

## 6. 模型权重与 NDK

- 权重由首次引导下载，镜像与文件名在 `services/speech/SherpaModelSpec.kt`、`services/translation/GemmaModelSpec.kt`。
- llama.cpp 固定 tag `b10775`，由 CMake `FetchContent` 拉取；本机如需用本地源码，`export LLAMA_CPP_SRC=/path/to/llama.cpp`（该路径不入库），不要提交符号链接。
- CMake 参数见 `app/build.gradle.kts`（`GGML_NATIVE=OFF`、`armv8.2-a+dotprod` 默认；`-PduiyiArmArch=` 可切 8×8 repack 对比）。

## 7. 证据流程（已启用）

```bash
make test             # 强制重跑 JVM 单测（JUnit XML → app/build/test-results/）
git commit -am ...    # 证据要求 clean tree：先提交代码
make evidence-test    # 跑测 → JUnit XML 聚合 → 写 harness/evidence/<UTC>-tests-pass.json
make verify-claim     # 三值：PASS / FAIL / UNVERIFIED（无证据 = UNVERIFIED）
```

细节：`tools/evidence_from_junit.py` 负责计数（passed/failed/skipped），`tools/evidence.py` 绑定 commit 并要求 dirty=false。无证据的“已验证”按未验证处理；环境不可用时写“未验证 + 手动步骤”。

## 8. 门禁与 hooks

```bash
make check            # 文档 / 指令 / 计划静态门禁
make check-host       # 宿主静态：分层 + 卫生（CI 可跑）
make check-quality    # detekt + ktlint + Android Lint（baseline 起步；本机）
make verify-static    # check + 证据 schema + check-host
make verify-claim     # 证据三值判定
git config core.hooksPath .githooks   # 可选：启用 pre-push（SKIP_HARNESS_HOOK=1 可跳过）
```

CI（`.github/workflows/verify.yml`）只跑静态门禁（含 `check-host`）；单测、质量与真机验证在本机完成。

## 9. 文档规则

- 新增 `docs/*.md` 必须在 [`docs/README.md`](docs/README.md) 登记，否则 `make check` 失败。
- 现状与历史分开：历史原文进 `docs/_archive/`，只加日期与状态头，不改写正文。
- 不写本机绝对路径、设备序列号、密钥；提交前跑 `make check`。

## 10. 常见故障

| 现象 | 处置 |
| --- | --- |
| `SDK location not found` | 创建 `local.properties` 并写 `sdk.dir` |
| Gradle 插件/依赖解析失败（`Plugin ... was not found`） | 检查 `~/.gradle/gradle.properties` 是否指向已停止的本机代理；临时用 `-Dhttp.proxyHost= -Dhttps.proxyHost= -Dhttp.proxyPort= -Dhttps.proxyPort=` 覆盖，或修正全局配置 |
| CMake/NDK 报错或版本漂移 | 删 `app/.cxx/` 重构建；确认 NDK 由 AGP 下载 |
| Gradle 守护进程版本异常 | `./gradlew --stop` 后用 JDK 17–21 重跑 |
| 模型下载到 80 MB 就“完成” | 已知问题 D-3，见 [`docs/09-current-state.md`](docs/09-current-state.md) |
| 下载/识别不可用时提示不明确 | 记录到计划“未验证项”，不在文档里写成可用 |
