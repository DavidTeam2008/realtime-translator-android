#!/bin/sh
# 跑 JVM 单测并把 JUnit XML 转成 tests-pass 证据（要求 clean tree）。
# 流程：verify-unit.sh --rerun-tasks → tools/evidence_from_junit.py → tools/evidence.py write
set -eu
cd "$(dirname "$0")/.."

echo "[evidence] 跑单测（--rerun-tasks）..."
./scripts/verify-unit.sh --rerun-tasks

draft=$(mktemp -t duiyi-tests-pass.XXXXXX.json)
trap 'rm -f "$draft"' EXIT

echo "[evidence] JUnit XML → evidence 草稿"
python3 tools/evidence_from_junit.py \
  --xml 'app/build/test-results/testDebugUnitTest/*.xml' \
  --claim tests-pass \
  --command './scripts/verify-unit.sh' \
  --environment toolchain="JDK 17 / Gradle 8.10.2 / AGP 8.7.2" \
  --environment device="unit-jvm" \
  --environment suite="app testDebugUnitTest" \
  --notes "P4：JVM 单测证据；计数口径 = JUnit XML testcase 聚合" \
  --output "$draft"

echo "[evidence] 写入 harness/evidence/"
python3 tools/evidence.py write --from-json "$draft"
