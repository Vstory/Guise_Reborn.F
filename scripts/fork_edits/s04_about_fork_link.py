#!/usr/bin/env python3
"""关于页：在「查看源代码」（上游仓库）下面加一条指回 fork 仓库的入口。

上游关于页只有一条 GitHub 行指向 daxiaamu/Guise_Reborn；构建包再加一条指回 fork。
文案进字符串资源（默认英文 + values-zh），不硬编码在代码里，免得英文设备上蹦出中文。
"""

from __future__ import annotations

from _common import FORK_REPOSITORY, apply, parse_args

STRINGS = "app/src/main/res/values/strings.xml"
STRINGS_ZH = "app/src/main/res/values-zh/strings.xml"
SETTING_SCREEN = "app/src/main/java/com/houvven/guise/ui/routing/launcher/SettingScreen.kt"

# 锚在上游已有的「查看源代码」条目上：整块连带 LinkSettingItem( 一起匹配，
#   单看 url = ... 那行在文件里只此一处，但带上下文更稳，上游挪动条目时能立刻发现。
UPSTREAM_LINK_BLOCK = """        LinkSettingItem(
            icon = Icons.Default.Code,
            title = stringResource(R.string.settings_view_source_code),
            summary = stringResource(R.string.settings_view_source_code_summary),
            url = "https://github.com/daxiaamu/Guise_Reborn",
        )
"""

FORK_LINK_BLOCK = f"""        LinkSettingItem(
            icon = Icons.Default.AccountTree,
            title = stringResource(R.string.settings_fork_source_code),
            summary = stringResource(R.string.settings_fork_source_code_summary),
            url = "https://github.com/{FORK_REPOSITORY}",
        )
"""


def build_edits() -> list[tuple[str, str, str, int]]:
    return [
        # 图标 import 必须一起加，否则 AccountTree 解析不到 —— 编译器不会替我们补。
        (
            SETTING_SCREEN,
            "import androidx.compose.material.icons.filled.Code\n",
            "import androidx.compose.material.icons.filled.AccountTree\n"
            "import androidx.compose.material.icons.filled.Code\n",
            1,
        ),
        (SETTING_SCREEN, UPSTREAM_LINK_BLOCK, UPSTREAM_LINK_BLOCK + FORK_LINK_BLOCK, 1),
        (
            STRINGS,
            '    <string name="settings_view_source_code_summary">View source code on GitHub and submit issues</string>\n',
            '    <string name="settings_view_source_code_summary">View source code on GitHub and submit issues</string>\n'
            '    <string name="settings_fork_source_code">Fork repository</string>\n'
            '    <string name="settings_fork_source_code_summary">Source code and builds of this fork (Guise.F)</string>\n',
            1,
        ),
        (
            STRINGS_ZH,
            '    <string name="settings_view_source_code_summary">在Github查看源代码，提交issues</string>\n',
            '    <string name="settings_view_source_code_summary">在Github查看源代码，提交issues</string>\n'
            '    <string name="settings_fork_source_code">Fork 项目地址</string>\n'
            '    <string name="settings_fork_source_code_summary">本 fork 的源码与构建产物</string>\n',
            1,
        ),
    ]


def main() -> int:
    args = parse_args(__doc__.splitlines()[0])
    apply(build_edits(), dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
