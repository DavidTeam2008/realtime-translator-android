#!/usr/bin/env python3
"""Host-specific hygiene guard: tracked build artifacts, absolute symlinks,
local machine paths, oversized tracked files, and root-file allowlist.

Configuration: <root>/harness/config.json -> "hygiene":
  trackedArtifactGlobs, rootAllowlist, localPathPatterns, maxTrackedFileBytes,
  skipLocalPathScan (path prefixes where historical local paths are tolerated)

Usage:
    python3 tools/check_hygiene.py [--root PATH]

Exit codes: 0 ok; 1 violations. Standard library only.
"""
from __future__ import annotations

import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

CONFIG_REL = Path("harness") / "config.json"
TEXT_SUFFIXES = {
    ".md", ".markdown", ".kt", ".kts", ".java", ".xml", ".json", ".yml", ".yaml",
    ".sh", ".bash", ".zsh", ".properties", ".txt", ".toml", ".gradle", ".cpp",
    ".c", ".h", ".hpp", ".cmake", ".pro", ".gitignore", ".cfg", ".ini",
    ".py", ".mjs", ".js", ".ts",
}


def git(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"[FAIL] git {' '.join(args)} 失败：{proc.stderr.strip()}")
    return proc.stdout


def load_config(root: Path) -> dict:
    path = root / CONFIG_REL
    if not path.is_file():
        raise SystemExit(f"[FAIL] 缺少配置：{CONFIG_REL.as_posix()}")
    data = json.loads(path.read_text(encoding="utf-8"))
    hygiene = data.get("hygiene")
    if not isinstance(hygiene, dict):
        raise SystemExit("[FAIL] harness/config.json 缺少 hygiene 配置")
    return hygiene


def tracked_files(root: Path) -> list[str]:
    return [line for line in git(root, "ls-files", "-z").split("\0") if line]


def main(argv: list[str]) -> int:
    root = Path(__file__).resolve().parent.parent
    rest = argv[1:]
    if rest and rest[0] == "--root" and len(rest) > 1:
        root = Path(rest[1]).resolve()
    hygiene = load_config(root)
    problems: list[str] = []

    artifact_globs = list(hygiene.get("trackedArtifactGlobs") or [])
    root_allowlist = set(hygiene.get("rootAllowlist") or [])
    local_patterns = []
    for pattern in hygiene.get("localPathPatterns") or []:
        if pattern.startswith("/") and pattern.endswith("/"):
            # 绝对路径目录：要求前面不是标识符字符，避免把 features/home/ 当成 /home/。
            local_patterns.append(re.compile(r"(?:^|[^A-Za-z0-9_.-])" + re.escape(pattern)))
        else:
            local_patterns.append(re.compile(pattern))
    skip_scan = tuple(hygiene.get("skipLocalPathScan") or ())
    max_bytes = int(hygiene.get("maxTrackedFileBytes") or 5 * 1024 * 1024)

    files = tracked_files(root)
    if not files:
        print("[FAIL] 仓库没有跟踪文件（git ls-files 为空）")
        return 1

    # 1) tracked build artifacts
    for relative in files:
        for pattern in artifact_globs:
            if fnmatch.fnmatch(relative, pattern) or fnmatch.fnmatch(Path(relative).name, pattern):
                problems.append(f"被跟踪的构建产物：{relative}（命中 {pattern}）")
                break

    # 2) root file allowlist
    for relative in files:
        if "/" not in relative and relative not in root_allowlist:
            problems.append(f"根目录文件不在 hygiene.rootAllowlist：{relative}")

    # 3) absolute symlinks
    ls_out = git(root, "ls-files", "-s", "-z")
    for entry in [item for item in ls_out.split("\0") if item]:
        meta, _, path = entry.partition("\t")
        parts = meta.split()
        if len(parts) < 3:
            continue
        mode, sha = parts[0], parts[1]
        if mode != "120000":
            continue
        try:
            target = git(root, "cat-file", "-p", sha).strip()
        except SystemExit:
            continue
        if target.startswith("/"):
            problems.append(f"绝对符号链接：{path} -> {target}")

    # 4) local machine paths in tracked text files
    for relative in files:
        if any(relative.startswith(prefix) for prefix in skip_scan):
            continue
        suffix = Path(relative).suffix or Path(relative).name
        if suffix not in TEXT_SUFFIXES:
            continue
        path = root / relative
        if not path.is_file() or path.is_symlink():
            continue
        if path.stat().st_size > max_bytes:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pattern in local_patterns:
            match = pattern.search(text)
            if match:
                problems.append(f"本机路径入库：{relative}（命中 {match.group(0)}）")
                break

    # 5) oversized tracked files
    for relative in files:
        path = root / relative
        if path.is_file() and not path.is_symlink() and path.stat().st_size > max_bytes:
            problems.append(f"跟踪文件超过 {max_bytes} bytes：{relative}")

    if problems:
        for item in problems:
            print(f"[FAIL] {item}")
        print(f"[FAIL] check_hygiene 发现 {len(problems)} 个卫生问题")
        return 1
    print(f"[OK] 卫生检查：{len(files)} 个跟踪文件，0 违规")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
