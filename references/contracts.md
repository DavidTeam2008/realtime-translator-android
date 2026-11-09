# 契约与边界（本仓铁律）

> 触发：改跨层代码/引擎/任务/存储/UI 前读。定位 [`../AGENTS.md`](../AGENTS.md)｜验证见 [`verification.md`](verification.md)

## 1. 依赖方向

- 规则：features 只依赖 domain 协议与 services 接口；domain 不 import Android/AndroidX/Room；services 不引用 ViewModel；designsystem 仅 UI 原子。
- 理由：可替换、并发可测。
- 检查：§8 grep 前两条空；评审 diff。存量例外不扩大，P4 分层守卫基线化。

## 2. 翻译/语音边界

- 规则：翻译只在 services/translation；语音只在 services/speech；页面不 new 引擎，经协议+Hilt 注入。
- 理由：单引擎与资源集中。
- 检查：§8 第三条空；评审 AppBindings。

## 3. 任务语义

- 规则：显式「新→结束」；暂停只停麦克风；空任务结束即删、不进历史；只有 Ended 进历史；杀进程可恢复。
- 理由：任务=一次完整工作。
- 检查：`TaskSessionController`、`RoomStore.list`、`InMemoryTaskStoreTest`。

## 4. 实时字幕以内存为准

- 规则：现场字幕/译文在 ViewModel 内存，落盘异步（250ms 批量）；View 不直读 Room。
- 理由：UI 不等 I/O。
- 检查：features 不 import Room DAO；写入只经 `TaskStore.append`。

## 5. 诚实原则

- 规则：桩功能不得在 UI 假装可用；总结/音频策略/语言能力三处桩须标：实现/撤 UI/未验证。
- 理由：假能力比缺功能伤信任。
- 检查：评审 UI 入口；对照 05-known-issues 桩清单。

## 6. 测试只增不减

- 规则：不改既有断言；基线 65 单测/skip 0，删测试即红。
- 理由：防回归。
- 检查：`./scripts/verify-unit.sh`；floor 见 [baseline](../harness/test-baseline.json)。

## 7. 证据与文档

- 证据：声明附命令/退出码/环境/证据 ID；无证据或 `make verify-claim` 非 PASS = 未验证；取证需 clean tree。
- 文档：当前/历史两态（历史进 `docs/_archive/`，只加状态头）；索引在 [docs/README](../docs/README.md)；不写本机路径/设备 ID/密钥。
- 检查：`make check`、`make verify-claim`。

## 8. 静态自检

```sh
D=app/src/main/java/com/duiyi/android
grep -rEn "^import (android|androidx)" $D/domain
grep -rn ViewModel $D/services
grep -rn LlamaNative $D/features
```
