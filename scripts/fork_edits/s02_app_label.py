#!/usr/bin/env python3
"""显示名：app_name 追加 fork 后缀（Guise → Guise.F）。"""

from __future__ import annotations

from _common import apply, parse_args

APP_NAME_XML = "app/src/main/res/values/strings.xml"


def build_edits(suffix: str) -> list[tuple[str, str, str, int]]:
    return [
        # 显示名：launcher、LSPosed 模块列表、系统设置里的应用名都读这个。只**追加** fork 后缀，
        #   不换名字 —— 换了等于让人分不清这还是不是原来那个模块。
        #   本工程 app_name 是 translatable="false"，只在 values/ 有一份，没有 locale 副本要同改。
        (
            APP_NAME_XML,
            '<string name="app_name" translatable="false">Guise</string>',
            f'<string name="app_name" translatable="false">Guise{suffix}</string>',
            1,
        ),
    ]


def main() -> int:
    args = parse_args(__doc__.splitlines()[0])
    apply(build_edits(args.label_suffix), dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
