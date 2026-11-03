#!/usr/bin/env python3
"""收尾反查：改写跑完后，从结果侧确认 fork 身份确实落地，而不是只信每条改写自己报的成功。"""

from __future__ import annotations

from _common import (
    FORK_REPOSITORY,
    REPO_ROOT,
    UPSTREAM_REPOSITORY,
    fail,
    parse_args,
)

BUILD_GRADLE = "app/build.gradle.kts"
APP_NAME_XML = "app/src/main/res/values/strings.xml"
APP_UPDATER = "app/src/main/java/com/houvven/guise/update/AppUpdater.kt"
SETTING_SCREEN = "app/src/main/java/com/houvven/guise/ui/routing/launcher/SettingScreen.kt"


def main() -> int:
    args = parse_args(__doc__.splitlines()[0])
    if args.dry_run:
        print("[dry-run] 改写尚未发生，跳过身份残留校验")
        return 0

    def text(rel: str) -> str:
        return (REPO_ROOT / rel).read_text(encoding="utf-8")

    problems: list[str] = []
    if f'applicationId = "{args.app_id}"' not in text(BUILD_GRADLE):
        problems.append(f"{BUILD_GRADLE}: applicationId 不是 {args.app_id}")
    if f">Guise{args.label_suffix}<" not in text(APP_NAME_XML):
        problems.append(f"{APP_NAME_XML}: 显示名不是「原名 + {args.label_suffix}」")
    if UPSTREAM_REPOSITORY in text(APP_UPDATER):
        problems.append(f"{APP_UPDATER}: 更新源仍残留上游仓库路径")
    screen = text(SETTING_SCREEN)
    if f"https://github.com/{FORK_REPOSITORY}" not in screen:
        problems.append(f"{SETTING_SCREEN}: 关于页缺 fork 仓库入口")
    if "settings_fork_source_code" not in screen:
        problems.append(f"{SETTING_SCREEN}: 关于页入口没有引用 fork 文案资源")

    if problems:
        for p in problems:
            print(f"::error::{p}", file=None)
        fail("fork 身份残留校验未通过")
    print("身份残留校验通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
