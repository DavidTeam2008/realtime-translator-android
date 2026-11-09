#!/bin/sh
# 跑 Android JVM 单元测试（JUnit XML 会写到 app/build/test-results/testDebugUnitTest/）。
# 优先用仓库本地工具链 shim（自动挑 JDK 17–21）；没有 shim 时直接调 Gradle wrapper。
# 证据链：tools/evidence_from_junit.py + tools/evidence.py write --from-json（见 harness/README.md）。
set -eu
cd "$(dirname "$0")/.."
if [ -x scripts/gradlew-local.sh ]; then
  exec scripts/gradlew-local.sh testDebugUnitTest "$@"
fi
exec ./gradlew testDebugUnitTest "$@"
