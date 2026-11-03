#!/usr/bin/env python3
"""应用内更新源：四处在用 URL 全部指向 fork 仓库。"""

from __future__ import annotations

from _common import FORK_REPOSITORY, UPSTREAM_REPOSITORY, apply, parse_args

APP_UPDATER = "app/src/main/java/com/houvven/guise/update/AppUpdater.kt"


def build_edits() -> list[tuple[str, str, str, int]]:
    # 不指向 fork 的话，fork 包会拿着上游最新版的元数据去比版本、点「更新」还会下载上游 APK
    #   （包名/签名都不同，装必失败）。配套的 latest-*.json 也放在 fork 的 main 上。
    return [
        (
            APP_UPDATER,
            f'const val RELEASES_URL = "https://github.com/{UPSTREAM_REPOSITORY}/releases"',
            f'const val RELEASES_URL = "https://github.com/{FORK_REPOSITORY}/releases"',
            1,
        ),
        (
            APP_UPDATER,
            f'private const val MANIFEST_REPOSITORY_PATH = "{UPSTREAM_REPOSITORY}@main"',
            f'private const val MANIFEST_REPOSITORY_PATH = "{FORK_REPOSITORY}@main"',
            1,
        ),
        (
            APP_UPDATER,
            f'"https://api.github.com/repos/{UPSTREAM_REPOSITORY}/contents/$manifestName?ref=main",',
            f'"https://api.github.com/repos/{FORK_REPOSITORY}/contents/$manifestName?ref=main",',
            1,
        ),
        (
            APP_UPDATER,
            f'"https://raw.githubusercontent.com/{UPSTREAM_REPOSITORY}/main/$manifestName",',
            f'"https://raw.githubusercontent.com/{FORK_REPOSITORY}/main/$manifestName",',
            1,
        ),
    ]


def main() -> int:
    args = parse_args(__doc__.splitlines()[0])
    apply(build_edits(), dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
