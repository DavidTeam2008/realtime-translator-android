# 07 端侧大模型：TranslateGemma 4B 的选型、机制与实测

> 本文是**当前技术资产**：描述 Android 对译里真正跑在手机上的大模型路径。数字均标注测量日期与设备；无法回溯到当次测量的标「历史记录，未复测」。
> 相关：延迟归因见 [`08-latency.md`](08-latency.md)；现状速览见 [`09-current-state.md`](09-current-state.md)；运行时流水线见 [`04-runtime.md`](04-runtime.md)；选型取舍见 [`03-decisions.md`](03-decisions.md)；后续排期见 [`06-roadmap.md`](06-roadmap.md)；索引见 [`README.md`](README.md)。

## 1. 它在产品里干什么

端侧大模型只做翻译，不碰麦克风。麦克风→Silero VAD→SenseVoice 整段听写→语种/脚本路由→字幕；只有「面对面」和「同声传译」会把 final 文本送进 4B 模型，「会议记录」只转写、不翻译。

| 模块 | 听写 | 大模型 |
| --- | --- | --- |
| 面对面 | SenseVoice，中英都听 | 中→英、英→中各译一次，写到对面一侧 |
| 同声传译 | SenseVoice，锁现场语种 | 源语→目标语，覆盖字幕；可选系统 TTS |
| 会议记录 | SenseVoice | 不翻译 |
| 任务历史 | 无 | 无（读已存文本） |

听写与翻译是两条栈：SenseVoice 由 sherpa-onnx 推理，翻译由 llama.cpp 推理，两者都在 CPU 上，且**共用同一批大核**——这条共享资源是延迟问题的核心背景（见 [`08-latency.md`](08-latency.md) 的 ComputeGate 一节）。

## 2. 选型与运行方式

| 项 | 取值 |
| --- | --- |
| 模型 | Google **TranslateGemma 4B Instruct**，GGUF `Q4_K_M` |
| 权重 | `GemmaModelSpec`：`translategemma-4b-it.Q4_K_M.gguf`，`EXPECTED_BYTES = 2_489_909_760`（约 2.49 GB），`MIN_BYTES = 2_000_000_000` |
| 来源 | `mradermacher/translategemma-4b-it-GGUF`；镜像 `hf-mirror.com` 优先、`huggingface.co` 兜底 |
| 运行时 | llama.cpp tag `b10775` + ggml CPU；`CMakeLists.txt` 优先用 `third_party/llama.cpp`，缺失时 `FetchContent` 拉同 tag |
| 推理设备 | **全 CPU**：`n_gpu_layers = 0`，关 OpenCL / Hexagon / OpenMP，`flash_attn_type` 关闭、`offload_kqv = false` |
| 封装 | `app/src/main/cpp/llama_jni.cpp` → `libduiyi_llama.so`；Kotlin 侧 `LlamaNative`（JNI 声明）与 `GemmaTranslator`（Hilt 单例） |
| 线程 | `Threads = availableProcessors().coerceIn(2, 4)`，在 `pin_to_big_cores` 之后创建上下文 |

`CMakeLists.txt` 的关键编译开关：`GGML_NATIVE=OFF`、`GGML_OPENMP/BLAS/CUDA/VULKAN/METAL/OPENCL/HEXAGON=OFF`、`LLAMA_CURL/OPENSSL/BUILD_TESTS/BUILD_EXAMPLES/BUILD_SERVER/BUILD_TOOLS/BUILD_COMMON=OFF`、`BUILD_SHARED_LIBS=OFF`；Debug 也强制 `-O3 -DNDEBUG`（4B 在 `-O0` 下几乎跑不完 prompt）。`GGML_CPU_ARM_ARCH` 默认 `armv8.2-a+dotprod`，可用 gradle 属性 `-PduiyiArmArch=...` 切换（见 §7）。

模型下载与就绪由 `GemmaModelStore` 负责：`ensureReady` 走 `RemoteFileDownloader`（带 `minBytes` 校验），`isReady()` 用 `GemmaModelSpec.isComplete` 判尺寸，`modelPath()` 交给 JNI。**注意**：就绪判定用的是 `MIN_BYTES`（2.0 GB）而不是 `EXPECTED_BYTES`（2.49 GB），一个截断到 2.0–2.49 GB 的文件会被当成就绪、把失败推到 `llama_model_load_from_file`——与听写侧 D-3 同类（见 [`09-current-state.md`](09-current-state.md)）。

## 3. 模型架构要点

底座是 **Gemma 3** 的**解码器-only** Transformer（causal LM），不是经典 NMT 的编码器-解码器。下面这组结构数字来自 2026-09-07 荣耀真机自检日志（**历史记录，未复测**）：

| 项 | 值 | 含义 |
| --- | --- | --- |
| 参数量 | 3.88 B | 常称 4B |
| 层数 | 34 | llama.cpp 识别为 Gemma 3 4B |
| 训练上下文 | 131072 | 实际 `N_CTX = 1024`，字幕场景够用 |
| 词表 | SentencePiece，262208 | 中英日韩泰越都在内 |
| 注意力 | ISWA（交织滑动窗口），period≈6 | 少数层全量、其余层只看窗口；前缀缓存必须整份 `llama_state_*` 快照，不能按普通 LLaMA 剪 KV |
| 量化 | GGUF `Q4_K_M` | 只压权重；运行时 KV 仍是 FP16 |
| 采样 | greedy | 翻译要稳定，不用温度/top-p |
| 批 | `n_batch = n_ubatch = 64` | prefill 每次最多 64 token |

它是「把 prompt 当成没写完的文章继续补」：没有独立翻译层，翻译能力在权重和 prompt 里。因果 LM 推理因此总是两段——**prefill**（读 prompt，算 KV）和 **decode**（每次只追加 1 token，带宽绑定）。

## 4. 一次「译一句」的路径

Kotlin 侧在点「听」或引导完成后调用 `GemmaTranslator.prepare(pairs)`：

1. `GemmaModelStore.ensureReady` 下载/校验权重（下载进度先映射到 ≤ 0.97，预热完成后置 1）。
2. `ensureLoaded`：`LlamaNative.create(modelPath, N_CTX = 1024, threads)`，内部 `pin_to_big_cores` → `llama_model_load_from_file`（mmap，不整文件拷堆）→ `llama_init_from_model`（`n_gpu_layers=0`、greedy sampler、abort callback）→ 1 token BOS warmup → 清 KV。
3. 对每个语言对 `LlamaNative.warmPrefix(prefix)`：把模板 token 灌进 KV，再整份快照进「模板槽」（最多 2 个）。同传只需一个方向，面对面两个方向都要。

每句解析为 **prefix + suffix**（`TranslateGemmaPrompt.parts`）：

- prefix：固定的系统指令（源/目标语言名与 code + “Produce only the … translation …” + “Please translate …”），同语言对每句完全一致；
- suffix：本次源句 + `<end_of_turn>\n<start_of_turn>model\n`。

`LlamaNative.generate` 的步骤：

1. 分别 tokenize `prefix` 与 `prefix + suffix`，**校验整段 token 序列以 prefix token 为前缀**；SentencePiece 可能在子词边界切错，对不上就放弃缓存、整段重算（退回优化前路径，不报错）。
2. 投机命中检查：若早先 `prefillSource` 留下的「prefix + 源句除最后一个 token」快照命中，恢复它，只 decode 最后 1 个 token；否则恢复/重建模板槽，再 decode 整段 suffix。
3. greedy 循环：`llama_sampler_sample` 取 token，遇 EOG 停止；每生成一个 token 把它追加进 `handle->progress`（供 UI 轮询），再 decode 该 token 进入下一轮；上限由 `TranslateGemmaPrompt.maxOutputTokens(text)` 决定 = `(字符数 + 16).coerceIn(16, 64)`。
4. 生成期间 `GemmaTranslator` 调用 `ComputeGate.beginTranslation()` / `endTranslation()`，让语音路径决定是否暂停 partial 解码；外层有 180 s 超时，超时调用 `LlamaNative.abort`。
5. 结果经 `TranslateGemmaPrompt.sanitize` 清洗：去掉 `<start_of_turn>`、`Translation:` / `译文：` / `譯文：`、被模型自行加上的 `[背景]/[语境]/[Context]` 标签、`<end_of_turn>` 之后的解释、以及首尾成对引号。

`LlamaNative` 方法面：`create` / `warmPrefix` / `generate` / `progress` / `prefillSource` / `setVerboseLogging` / `abort` / `destroy`。

## 5. Prompt 模板与调用策略

- 语言：`AppLanguage` 六种（中/英/日/韩/泰/越），模板同时给语言名与 BCP-47 风格 code（如 `zh-Hans`、`en`）。
- **只译 final（当前默认）**：`enqueueTranslation` 在非 final 时直接返回；半句只做投机 prefill，不送生成。这样可以避免「半句译文乱跳」，代价是长句要等说话结束（见 [`08-latency.md`](08-latency.md) 的 D-2）。
- **增量翻译（`incrementalTranslation`，默认关）**：`StablePrefixTracker` 只在「最近两次 partial 未变 + 落在标点边界」时提交一个块，块结果只追加、不覆盖；质量风险与 A/B 方案见 [`08-latency.md`](08-latency.md)。
- **不再拼接上一句**：`previousSource` 参数仍保留在 `TranslateGemmaPrompt.parts` / `GemmaTranslator.translate` 签名里，但被标为 `@Suppress("UNUSED_PARAMETER")`，**不进入 prompt**。历史上把上一句塞 `[context]` 会被 4B 译成 `[背景]` 并串台。
- 输出上限：`maxOutputTokens` 按源句字符数封顶（16–64），短句少跑空循环，长句仍最多 64 token。

## 6. 关键机制

### 6.1 前缀 KV 快照（语言对级）

模板 token 的 KV 是纯函数，算一次可反复用。`llama_jni.cpp` 用两个 pinned 槽（`kMaxPrefixes = 2`）保存 `llama_state_get_data` 快照；命中则 `llama_state_set_data` 还原。槽 key 是模板 token 序列，FIFO 淘汰。面对面双向时两个槽分别放 en→zh / zh→en；同传只占一个。

### 6.2 投机 prefill（`prefillSource`）

partial 已给出「final 的长前缀」时，可提前把「模板 + 源句（除最后一个 token）」decode 进 KV 并快照到可淘汰的 `kMaxSpeculatives = 2` 槽；final 到达且 token 序列匹配时只 decode 最后 1 个 token。**必须留最后一个 token 给 `generate` 解码**：`llama_state_*` 只恢复 KV，而采样读的 logits 由 decode 产生，恢复后不 decode 会采到上一轮残留的 logits。`TranslationPump.speculate` 只在 pump 空闲（无排队、无 in-flight）时触发，避免投机和用户真正在等的翻译抢核。

### 6.3 生成 streaming

`generate` 每产出一个 token 就加锁更新 `handle->progress`；`LlamaNative.progress` 读出整段已生成文本；`TranslationPump` 每 120 ms 轮询一次、经 `onProgress` 只更新字幕，不写 transcript、不落盘。总生成时间不变，属于体感优化。

### 6.4 大核绑定

`pin_to_big_cores` 在模型加载与任何 decode 之前执行：枚举在线核，按 `/sys/devices/system/cpu/cpuN/cpu_capacity`（缺失则 `cpuinfo_max_freq`）降序取前 `n_threads` 个，`sched_setaffinity` 绑当前 JNI 线程；ggml 的工作线程随后从该线程创建，Linux 上继承 affinity。荣耀 ALP-AN00 上落到 X2 + 3×A710，A510 不参与 Gemma 推理（**历史记录，未复测**）。

### 6.5 Q4_K repack 与构建开关

dotprod 构建下 ggml 实际用 `q4_K_8x4` 内核（日志 `repack tensor blk.0.attn_q.weight with q4_K_8x4`）。`-PduiyiArmArch=armv8.6-a+dotprod+i8mm` 会切到 Q4_K 8×8 内核，可复现 A/B；**结论是不要用**（见 §7）。运行时会打印 `kernel cpu features: dotprod=… i8mm=…`，这是运行时 HWCAP，不是编译期断言。

## 7. 实测数字（标注日期与设备）

测量设备：**Honor X50 GT（ALP-AN00）**，骁龙 8+ Gen 1，16 GB；**2026-09-07 真机自检**。下表是 `TranslationSelfTestActivity` 的隔离自检：无麦克风、无 VAD、无并发 SenseVoice，**不能直接当端到端延迟**。

| 步骤 | 耗时 | 备注 |
| --- | --- | --- |
| `prepare`（加载 + 双向前缀预热） | 18049 ms | 加载约 8–11 s + 两方向各约 3 s |
| en→zh `How are you.` | 1075 ms | `prefix_ms=15` + `suffix_ms=373` + `gen_ms=670` |
| en→zh `It's very cute.` | 1145 ms | 短句 |
| zh→en `这个也不对呀。` | 1717 ms | 英文输出更长，decode 更久 |

「历史记录，未复测」：以上 4 行与 §3 的结构数字均为 2026-09 自检归档，本轮文档蒸馏（2026-11-10）未重新跑真机。

i8mm vs dotprod A/B（归档 §5.2；Honor ALP-AN00，两次构建各跑 3 轮自检，**历史记录，未复测**）：

| 指标 | dotprod 中位 | i8mm 中位 | 变化 |
| --- | --- | --- | --- |
| 生成（短输出） | 437 ms | 470 ms | +8% |
| 生成（中输出） | 418 ms | 469 ms | +12% |
| 生成（长输出） | 840 ms | 1102 ms | +31% |
| 整句 zh→en | 1298 ms | 1605 ms | +24% |
| 源句 prefill（suffix=9） | 465 ms | 374 ms | −20% |
| 源句 prefill（suffix=10） | 436 ms | 506 ms | +16% |

结论：生成是每句大头而 i8mm 全面变慢，默认保持 `armv8.2-a+dotprod` / `q4_K_8x4`。原因推测：本负载几乎全是 GEMV（batch=1 解码），8×8 交错布局主要利好 GEMM；「指令级 2× 吞吐」推不出端到端更快。样本量有限（每组 3 轮、单轮 `gen_ms` 波动约 ±20%），结论依赖长输出档与总量指标的一致方向。

## 8. 风险与未验证

- **只在 Honor ALP-AN00 上测过**：其他 SoC（尤其大小核布局不同、无 dotprod、或小核不支持 I8MM 的设备）的线程绑核与内核选择未验证。
- **prefill 命中/预热收益是历史记录**：`prefix_ms=15`、prefill `373 ms` 等来自 2026-09 自检；2026-11 未复测。`TranslationPump` 的投机 prefill 有代码但**尚未有真机收益数据**。
- **模型版本可复现性**：`third_party/llama.cpp` 当前是绝对符号链接，换机可能静默走 `FetchContent`（同 tag 但来源不同）；该问题列入 P3 清洁（见 [`06-roadmap.md`](06-roadmap.md) 与 [`09-current-state.md`](09-current-state.md) D-6）。
- **权重就绪判定偏宽**：`MIN_BYTES` 2.0 GB < `EXPECTED_BYTES` 2.49 GB，截断文件可能被当作就绪（同类问题 D-3）。
- **抢核与 ComputeGate 的取舍**：生成期默认跳过 partial 解码，换 Gemma 不被抢核，代价是另一侧「正在说…」实时原文短暂停更；该假设**未经真机 A/B 测量**（见 [`08-latency.md`](08-latency.md)）。
- **会议模块不会常驻模型**：`MeetingViewModel` 进入/开始听写时 `translator.release()`，回面对面需重新 `prepare`（可能再付一次加载时间）；这是「把大核还给听写」的取舍，UI 尚未显式提示。
- **场景差异**：同传/面对面都把 4B 当唯一翻译器；专用小模型分流仍属评估项（见 [`06-roadmap.md`](06-roadmap.md)）。

## 9. 参考实现位置

| 主题 | 位置 |
| --- | --- |
| 模型规格/下载/就绪 | `services/translation/GemmaModelSpec.kt`、`GemmaModelStore.kt` |
| 加载/预热/生成/超时 | `services/translation/GemmaTranslator.kt` |
| Prompt 拆分/sanitize/输出上限 | `services/translation/TranslateGemmaPrompt.kt` |
| JNI 前缀快照/投机/绑核/生成循环 | `app/src/main/cpp/llama_jni.cpp`、`services/translation/LlamaNative.kt` |
| 编译参数（`-O3`、架构、关后端） | `app/src/main/cpp/CMakeLists.txt`、`app/build.gradle.kts` |
| 串行队列/投机入口/streaming 轮询 | `services/translation/TranslationPump.kt` |
| 生成期让出大核 | `services/ComputeGate.kt` |
| 自检（隔离 Gemma 计时） | `debug/TranslationSelfTestActivity.kt` |
