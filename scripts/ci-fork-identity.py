#!/usr/bin/env python3
# SCRIPT_VERSION=2.0.0
"""CI 专用：依次跑 fork 改写脚本，把 runner 工作区改成 fork 身份，仓库源码一行都不落库。

每项改动一个脚本，放在 scripts/fork_edits/（文件名前缀即执行顺序）；本文件只负责按序调用，
任一脚本失败即中止 —— 各脚本自己校验「期望原文命中几次」，上游改了写法就不会静默漏改。

用法：
    python3 scripts/ci-fork-identity.py --app-id com.houvven.guise.fork --label Guise.F
    python3 scripts/ci-fork-identity.py --dry-run
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EDITS_DIR = REPO_ROOT / "scripts" / "fork_edits"

DEFAULT_APP_ID = "com.houvven.guise.fork"
DEFAULT_LABEL = "Guise.F"
DEFAULT_LABEL_SUFFIX = ".F"

UPSTREAM_APP_ID = "com.houvven.guise"

# 同一批源码文件被多个步骤依次改写（strings.xml 被 02 / 04 各改一处，
#   SettingScreen.kt 被 04 改两处），锚的片段互不重叠；顺序固定下来最省心，最后一步从结果反查残留。
STEPS = (
    ("s01_package_id.py", "包名"),
    ("s02_app_label.py", "显示名"),
    ("s03_update_source.py", "应用内更新源"),
    ("s04_about_fork_link.py", "关于页 fork 入口"),
    ("s99_identity_check.py", "身份残留校验"),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--app-id", default=DEFAULT_APP_ID)
    parser.add_argument("--label", default=DEFAULT_LABEL)
    parser.add_argument("--label-suffix", default=DEFAULT_LABEL_SUFFIX)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not re.fullmatch(r"[A-Za-z0-9._]+", args.app_id):
        print(f"::error::--app-id 不合法：{args.app_id!r}", file=sys.stderr)
        return 1
    if args.app_id == UPSTREAM_APP_ID:
        print(f"::error::--app-id 必须与上游包名 {UPSTREAM_APP_ID} 不同（否则装不上/顶掉上游）",
              file=sys.stderr)
        return 1
    # 它进 APK 文件名与下载 URL
    if not re.fullmatch(r"[A-Za-z0-9._-]+", args.label):
        print(f"::error::--label 只允许 A-Za-z0-9._-：{args.label!r}", file=sys.stderr)
        return 1
    if args.label != f"Guise{args.label_suffix}":
        print(f"::error::--label 与显示名不同源：显示名会是 Guise{args.label_suffix}，"
              f"产物名前缀却是 {args.label!r}", file=sys.stderr)
        return 1

    for index, (name, title) in enumerate(STEPS, 1):
        path = EDITS_DIR / name
        if not path.is_file():
            print(f"::error::缺少改写脚本 {path.relative_to(REPO_ROOT)}", file=sys.stderr)
            return 1
        print(f"[{index}/{len(STEPS)}] {title}（{name}）", flush=True)
        cmd = [
            sys.executable,
            str(path),
            "--app-id",
            args.app_id,
            "--label",
            args.label,
            "--label-suffix",
            args.label_suffix,
        ]
        if args.dry_run:
            cmd.append("--dry-run")
        if subprocess.run(cmd, cwd=REPO_ROOT).returncode != 0:
            print(f"::error::{name} 失败，中止", file=sys.stderr)
            return 1

    print(f"已改写为 fork 身份：appId={args.app_id} 产物名前缀={args.label} "
          f"显示名=Guise{args.label_suffix}（仅工作区，不入库）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
