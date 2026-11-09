#!/bin/sh
# 选一个 Gradle 可用的 JDK（17–21）并调用仓库 wrapper。
# 原因：Kotlin 2.0.21 无法解析 JDK 25（IllegalArgumentException: 25.0.2），
#       且 AGP 8.7.2 只在约 ≤JDK 21 上验证过。
# 机器相关路径不入库：请在环境里设置 ANDROID_HOME / JAVA_HOME（或用 local.properties 的 sdk.dir）。
set -eu
ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)

java_ok() {
  [ -n "${1:-}" ] && [ -x "$1/bin/java" ] && "$1/bin/java" -version 2>&1 | grep -qE '"(1\.)?(1[0-9]|2[01])'
}

# ANDROID_HOME 优先环境变量，其次 local.properties 的 sdk.dir
if [ -z "${ANDROID_HOME:-}" ] && [ -f "$ROOT/local.properties" ]; then
  sdk=$(sed -n 's/^sdk\.dir=//p' "$ROOT/local.properties" | head -n 1)
  if [ -n "$sdk" ]; then ANDROID_HOME=$sdk; export ANDROID_HOME; fi
fi

# JAVA_HOME：环境里给的是 17–21 就直接用；否则在常见位置找 17/21（避免 JDK 24/25 的坑）
if java_ok "${JAVA_HOME:-}"; then
  :
else
  found=""
  for candidate in "$HOME"/.gradle/jdks/*/jdk-17*/Contents/Home \
                   "$HOME"/.gradle/jdks/*/jdk-21*/Contents/Home \
                   "$HOME"/Library/Java/JavaVirtualMachines/*17*/Contents/Home \
                   "$HOME"/Library/Java/JavaVirtualMachines/*21*/Contents/Home \
                   /Library/Java/JavaVirtualMachines/*17*/Contents/Home \
                   /Library/Java/JavaVirtualMachines/*21*/Contents/Home; do
    if java_ok "$candidate"; then found=$candidate; break; fi
  done
  if [ -n "$found" ]; then
    JAVA_HOME=$found
    export JAVA_HOME
  elif [ -n "${JAVA_HOME:-}" ]; then
    echo "warning: JAVA_HOME=$JAVA_HOME 不是 JDK 17–21；Kotlin 2.0.21 可能报 IllegalArgumentException。" >&2
  else
    echo "error: 未找到 JDK 17–21；请设置 JAVA_HOME（Kotlin 2.0.21 不支持 JDK 25）。" >&2
    exit 2
  fi
fi

exec "$ROOT/gradlew" "$@"
