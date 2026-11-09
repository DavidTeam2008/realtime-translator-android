# AGENTS.md · 对译 Duiyi Android

> 冷启动入口：只做定位与硬约束；事实以代码、测试与证据为准；细节读嵌套 `AGENTS.md` 与 docs。

## 1. 项目一句话

纯端侧 Android 实时翻译 App：面对面双屏、同声传译、会议记录、任务历史；**无后端、无账号、不上传，不把云 STT/云翻译当静默降级**。

分层：`app/`、`domain/`、`features/`、`services/`、`designsystem/`；依赖单向。

## 2. 硬事实

- Android 14+（minSdk 34，compile/target 35）、仅 `arm64-v8a`、竖屏。
- Kotlin 2.0.21 / AGP 8.7.2 / Gradle 8.10.2 wrapper / Compose / Hilt 2.52 / Room / KSP。
- 听写：荣耀/华为 → sherpa-onnx SenseVoice int8 + Silero VAD；其他厂商 → 系统 `SpeechRecognizer`（**非荣耀路径未真机验证**）。
- 翻译：llama.cpp + TranslateGemma 4B Q4_K_M（约 2.49 GB，全 CPU，进程级单例）。
- 单测基线 65（`harness/test-baseline.json` floor=65）。

## 3. 命令入口

| 用途 | 命令 |
| --- | --- |
| 静态门禁 | `make check` |
| 静态 + 证据校验 | `make verify-static` |
| 证据三值判定 | `make verify-claim` |
| 单测 | `./scripts/verify-unit.sh` |
| 新建计划 | `make plan TOPIC=<topic>` |
| 宿主质量（P4） | `make check-host` |

真机手工：`adb install -r app/build/outputs/apk/debug/app-debug.apk`；构建/诊断见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。

## 4. 阅读路由（按任务读段落）

- 接手：[`harness/plans/2026-11-10-android-adoption.md`](harness/plans/2026-11-10-android-adoption.md) → [`harness/README.md`](harness/README.md)。
- 架构/现状/决策：[`docs/02-architecture.md`](docs/02-architecture.md)、[`docs/09-current-state.md`](docs/09-current-state.md)、[`docs/03-decisions.md`](docs/03-decisions.md)。
- 规则 [`references/contracts.md`](references/contracts.md)；验证 [`references/verification.md`](references/verification.md)；分级/红队 [`references/workflow.md`](references/workflow.md)。
- 文档 [`docs/README.md`](docs/README.md) / [`docs/AGENTS.md`](docs/AGENTS.md)；状态目录 [`harness/AGENTS.md`](harness/AGENTS.md)。

## 5. 铁律（可执行）

1. **依赖单向**：`domain` 不依赖 Android/上层；`services` 不引用 `features`；`features` 只经 `domain` 与 `harness/config.json` 里 `layers` 允许的接缝。
2. **翻译只在 services**：`GemmaTranslator`/`TranslationPump` 是唯一入口，UI/VM 不直接调 llama JNI。
3. **单一语音引擎**：每进程一个听写引擎；荣耀/华为走 SenseVoice，其他厂商走系统识别器；不并行起第二路。
4. **任务语义**：显式“新任务 → 结束”；只有 ended 进历史；空任务结束即删；暂停只停麦克风；进后台停听不停任务。
5. **实时字幕以内存为准**：`PaneState` 是实时事实，Room 异步落盘；View 不直读数据库。
6. **禁静默云降级**：没有后端/上传；能力不可用就提示“本机不可用”。
7. **桩功能不假装可用**：未实现能力（如 `HonestSummarizer`）显式标不可用，不得演示成可用。
8. **测试只增不减**：不删/不改既有断言；`unit.floor=65` 由 `make verify-claim` 机检，删测试视为回归。
9. **不提交本机状态**：本机绝对路径、设备 ID/序列号、密钥、`local.properties`、构建产物不入库。
10. **证据与文档状态**：完成声明附命令/退出码/环境与 evidence id；docs 当前/历史状态不混写。

## 6. 分级与完成协议

- L0 文档/注释/单文件小改：直接做，跑 `make check`。
- L1 单模块修复/补测试：先写 5–10 行短方案，做完即验证。
- L2 跨模块/规则/CI/发布：完整方案 + 确认；并发/持久化/发布走独立只读复核。
- 完成 = 验收判据满足 + 证据已记录 + `make verify-static` PASS + 计划已更新；未运行写“未验证”与原因。
- 同一失败修复 2 次仍不过 / 子任务 3 轮无进展：停止上报。
