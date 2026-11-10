# 对译 Duiyi Android · harness 门禁（standard profile）
# 由 harness-kit 0.2.3 渲染；路径 / 命令 / 预算的唯一来源是 harness/config.json。
# 目标已有 Makefile 时本文件被写成 Makefile.harness，请在原 Makefile 末尾加：include Makefile.harness
# 宿主目标（check-quality / test / evidence-test）不属于 kit 渲染，由项目维护。

.PHONY: help check check-evidence check-host check-quality verify-static verify-claim test evidence-test plan

help: ## 显示可用目标
	@echo "对译 Duiyi Android · harness 目标"
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  make %-18s %s\n", $$1, $$2}'

check: ## 文档 + 指令 + 计划静态门禁
	@python3 tools/check_docs.py
	@python3 tools/check_agents.py
	@python3 tools/check_plan.py

check-evidence: ## 证据 schema 校验
	@python3 tools/evidence.py validate

check-host: ## 宿主卫生 / 分层守卫（未配置 hygiene/layers 时 SKIP）
	@python3 tools/check_hygiene.py
	@python3 tools/check_layers.py

check-quality: ## 宿主代码质量：detekt + ktlint + Android Lint（需 JDK 17–21 / Android SDK）
	@scripts/gradlew-local.sh detekt ktlintCheck lintDebug --console=plain

verify-static: check check-evidence check-host ## 本地静态门禁（含证据与宿主检查）

verify-claim: ## 证据三值判定（PASS / FAIL / UNVERIFIED）
	@python3 tools/verify_claim.py --all

test: ## JVM 单测（JUnit XML 写到 app/build/test-results/）
	@./scripts/verify-unit.sh --rerun-tasks

evidence-test: ## 生成 tests-pass 证据（要求 clean tree；先 make test 自动跑）
	@./scripts/evidence-unit.sh

plan: ## 新建计划：make plan TOPIC=<topic>
	@test -n "$(TOPIC)" || { echo "用法：make plan TOPIC=<topic>"; exit 2; }
	@python3 tools/check_plan.py new "$(TOPIC)"
