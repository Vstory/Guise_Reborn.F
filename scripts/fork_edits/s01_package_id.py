#!/usr/bin/env python3
"""包名：applicationId 改成 fork 形态。"""

from __future__ import annotations

from _common import apply, parse_args

BUILD_GRADLE = "app/build.gradle.kts"


def build_edits(app_id: str) -> list[tuple[str, str, str, int]]:
    return [
        # 只改 applicationId（最终包名），不动 namespace：R 类、资源引用、类的全限定名都跟
        #   namespace 走，改它会让 manifest 里的 `.ui.MainActivity` 解析到不存在的类（能装、一开就崩）。
        #   代码里对自身包名的判断全部走 BuildConfig.APPLICATION_ID（HookInit / ContextAmbient），
        #   改这里即自动跟随。
        (BUILD_GRADLE, "        applicationId = namespace", f'        applicationId = "{app_id}"', 1),
    ]


def main() -> int:
    args = parse_args(__doc__.splitlines()[0])
    apply(build_edits(args.app_id), dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
