# 对译 Duiyi · Android

纯端侧 Android 实时翻译 App：面对面双屏对话、同声传译、会议记录、任务历史。

**全端侧承诺**：听写、翻译、任务都留在手机上；没有后端、没有账号、不上传音频；**不把云 STT / 云翻译当作静默降级**。能力在本机不可用时明确提示，而不是偷偷走云。

## 四个模块

| 模块 | 行为 |
| --- | --- |
| 面对面 | 上下对半，上屏旋转 180°；语种当路由键；只译 final；可按偏好自动开听 |
| 同声传译 | 单栏正字；不自动开听；TTS 朗读需已接耳机，队列上限 2，按增量后缀朗读 |
| 会议记录 | 单语全文稿，不翻译；进入即卸载 4B 模型；超 2 万字提示结束并新开 |
| 任务历史 | 本地 Room；左滑删除；导出 UTF-8 txt 走系统分享 |

任务语义：新任务 → 听/暂停 → 结束任务；暂停 ≠ 结束；进后台停听写不停任务；空任务不进历史。

## 当前状态

- 主路径已在荣耀真机跑通；**端到端延迟约 2–2.7 s 是当前最大体验问题**，已知缺陷与实现现状见 [`docs/09-current-state.md`](docs/09-current-state.md)。
- 2026-11-10 起接入 harness-kit 0.2.2（standard），文档蒸馏、清洁与宿主传感器接线进行中：进度唯一真源见 [`harness/plans/2026-11-10-android-adoption.md`](harness/plans/2026-11-10-android-adoption.md)。

## 技术栈与最低系统

- Kotlin 2.0.21 · Jetpack Compose · Hilt 2.52 · Room · KSP；AGP 8.7.2 · Gradle 8.10.2 wrapper。
- 听写：sherpa-onnx **SenseVoice int8 + Silero VAD**；非荣耀厂商走系统 `SpeechRecognizer`（该路径未真机验证）。
- 翻译：**llama.cpp + TranslateGemma 4B Q4_K_M**（约 2.49 GB GGUF，全 CPU）。
- 最低系统：**Android 14（API 34）**；compile/target 35；仅 `arm64-v8a`；竖屏。

## 快速开始

前置：JDK **17–21**、Android SDK（compile/target 35）、NDK/CMake（AGP 管理）。

```bash
# 1) 写入本机 SDK 路径（local.properties 不入库）
#    sdk.dir=<你的 Android SDK 路径>
# 2) 构建 + 安装（wrapper 固定 Gradle 8.10.2）
./gradlew installDebug
# 3) 单测（纯 JVM，无需真机）
./scripts/verify-unit.sh
```

首次启动走引导：选择语言 → 授予麦克风权限 → 下载模型（SenseVoice ≈240 MB + TranslateGemma ≈2.49 GB，需要网络）→ 首页四个入口。

环境坑（Android Studio Quail 3 / JBR 25、Gradle 版本、`local.properties`、真机与诊断页）见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。

## 文档入口

| 文档 | 内容 |
| --- | --- |
| [`docs/README.md`](docs/README.md) | 文档索引：当前文档与历史档案 |
| [`docs/09-current-state.md`](docs/09-current-state.md) | 实现现状、已知缺陷、当前优先级 |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | 环境、构建、单测、真机、证据流程 |
| [`HARNESS.md`](HARNESS.md) | harness 地图：五子系统落点、计划与证据流程、门禁边界 |

## 质量与 harness

```bash
make check            # 文档 / 指令 / 计划静态门禁
make verify-static    # 再加证据 schema 校验
make verify-claim     # 证据三值判定（PASS / FAIL / UNVERIFIED）
./scripts/verify-unit.sh   # JVM 单测（基线 65，只增不减）
```

- 静态门禁在 CI（`.github/workflows/verify.yml`，ubuntu）与本地 `pre-push` 均可用；单测与真机验证在本机执行。
- 完成声明必须有证据或明确写“未验证”；计划与证据见 `harness/`。

## 隐私

- 无账号、无后端；音频与文字稿不出设备（模型文件与任务数据都在本机）。
- 麦克风权限仅用于听写；识别与翻译全部在设备端完成。
- 诊断日志只在 debug 包内生成，不自动上传。

## License

本仓库暂未随仓库提供 `LICENSE` 文件；对外分发、二次引用或商用前需与维护者确认许可（未决，见 active 计划）。
