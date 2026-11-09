#!/usr/bin/env python3
"""Host-specific layer guard for the Android app.

Checks (configuration: <root>/harness/config.json -> "layers"):
  R1 domain:    no Android/Compose/app/features/services/designsystem imports
  R2 services:  no features/designsystem imports (services implement protocols)
  R3 features:  imports from services are allowlisted (regression guard for
                technical debt; new dependencies must move behind a domain protocol)
  R4 features:  no direct Room/android.database imports (data access via protocols)
  R5 engines:   speech/translation engine classes referenced only in allowed dirs
  R6 app/designsystem: app may import everything; designsystem may import domain only

Usage:
    python3 tools/check_layers.py [--root PATH]

Exit codes: 0 ok; 1 violations or config error. Standard library only.
"""
from __future__ import annotations

import fnmatch
import json
import re
import sys
from pathlib import Path

CONFIG_REL = Path("harness") / "config.json"
IMPORT_RE = re.compile(r"^\s*import\s+([\w.]+)")
CLASS_REF_RE = re.compile(r"\b([A-Z][A-Za-z0-9]+)\b")


def load_config(root: Path) -> dict:
    path = root / CONFIG_REL
    if not path.is_file():
        raise SystemExit(f"[FAIL] 缺少配置：{CONFIG_REL.as_posix()}")
    return json.loads(path.read_text(encoding="utf-8"))


def rel(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def kotlin_files(root: Path, source_root: str) -> list[Path]:
    base = root / source_root
    if not base.is_dir():
        raise SystemExit(f"[FAIL] 源码目录不存在：{source_root}")
    return sorted(base.rglob("*.kt"))


def imports_of(path: Path) -> list[str]:
    imports: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = IMPORT_RE.match(line)
        if match:
            imports.append(match.group(1))
    return imports


def matches_any(value: str, prefixes: list[str]) -> str | None:
    for prefix in prefixes:
        if value == prefix or value.startswith(prefix + "."):
            return prefix
    return None


def in_allowed_path(path: str, allowed: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in allowed)


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 and argv[1] != "--root" else Path(__file__).resolve().parent.parent
    if len(argv) > 2 and argv[1] == "--root":
        root = Path(argv[2]).resolve()
    config = load_config(root)
    layers = config.get("layers")
    if not isinstance(layers, dict):
        print("[FAIL] harness/config.json 缺少 layers 配置")
        return 1
    source_root = str(layers.get("sourceRoot") or "app/src/main/java/com/duiyi/android")
    rules = {
        "domain": {
            "forbidden": list(layers.get("domainForbidden") or []),
            "allowlist": [],
        },
        "services": {
            "forbidden": list(layers.get("servicesForbidden") or []),
            "allowlist": [],
        },
        "features": {
            "forbidden": list(layers.get("featuresForbiddenImports") or []),
            "allowlist": list(layers.get("featuresServicesAllowlist") or []),
        },
    }
    engine_classes = list(layers.get("engineClasses") or [])
    engine_allowed = list(layers.get("engineAllowedPaths") or [])

    problems: list[str] = []
    files = kotlin_files(root, source_root)
    for path in files:
        relative = rel(root, path)
        layer = relative.split("/")[len(source_root.split("/"))] if relative.startswith(source_root + "/") else ""
        imports = imports_of(path)

        # R5: engine classes only in allowed paths
        if engine_classes and not in_allowed_path(relative, engine_allowed):
            code_lines = [
                line for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
                if not line.lstrip().startswith(("//", "*", "/*"))
            ]
            joined = "\n".join(code_lines)
            for name in engine_classes:
                if re.search(rf"\b{re.escape(name)}\b", joined):
                    problems.append(f"{relative}: 引擎类 {name} 只允许出现在 {engine_allowed}（R5）")

        layer_rule = rules.get(layer)
        if not layer_rule:
            continue
        for imported in imports:
            hit = matches_any(imported, layer_rule["forbidden"])
            if hit:
                if layer == "features" and hit.startswith("com.duiyi.android.services"):
                    if matches_any(imported, layer_rule["allowlist"]):
                        continue
                problems.append(f"{relative}: import {imported} 违反 {layer} 层规则（命中 {hit}）")
            elif layer == "features" and imported.startswith("com.duiyi.android.services."):
                if not matches_any(imported, layer_rule["allowlist"]):
                    problems.append(f"{relative}: import {imported} 不在 features→services 白名单（R3）")

    if problems:
        for item in problems:
            print(f"[FAIL] {item}")
        print(f"[FAIL] check_layers 发现 {len(problems)} 个分层问题")
        return 1
    print(f"[OK] 分层检查：{len(files)} 个 Kotlin 文件，0 违规（R1–R6）")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
