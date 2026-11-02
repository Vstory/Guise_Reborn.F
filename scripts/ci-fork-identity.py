#!/usr/bin/env python3
# SCRIPT_VERSION=1.0.0
# 母版：知识库 100_System/templates/ci-fork-identity.py（TEMPLATE_VERSION=1.0.0）
"""CI 专用：把 runner 工作区的包名、显示名与应用内更新源改写成 fork 形态，源码一行都不落库。

包名为什么落不进仓库：上游一旦改这些行，仓库里的 fork 值就是合并冲突；而 fork 身份只在出包
时才需要，故一律在 CI 工作区改写。

以「期望的原文 → 改写后」逐条声明，任一项找不到原文即整体失败：上游改了写法时必须回来同步，
不允许静默漏改（漏改的产物能装、能跑，只是装上去是上游那个应用、更新检查还去上游仓库）。

用法：
    python3 scripts/ci-fork-identity.py --app-id com.houvven.guise.fork --label Guise.F --label-suffix .F
    python3 scripts/ci-fork-identity.py --dry-run
    python3 scripts/ci-fork-identity.py --selftest
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_APP_ID = "com.houvven.guise.fork"
DEFAULT_LABEL = "Guise.F"
DEFAULT_LABEL_SUFFIX = ".F"

UPSTREAM_APP_ID = "com.houvven.guise"
UPSTREAM_REPOSITORY = "daxiaamu/Guise_Reborn"
FORK_REPOSITORY = "Vstory/Guise_Reborn.F"

APP_NAME_XML = 'app/src/main/res/values/strings.xml'
BUILD_GRADLE = 'app/build.gradle.kts'
APP_UPDATER = 'app/src/main/java/com/houvven/guise/update/AppUpdater.kt'


def build_edits(app_id: str, label: str, suffix: str) -> list[tuple[str, str, str]]:
    """(相对路径, 期望原文, 改写后)。原文出现次数不为 1 即失败。

    逐条写死原文本（不靠正则）是有意的：上游改了写法时宁可整体失败，也不许「改了一半」。

    label 不产生改写项 —— 本工程的 APK 名由 workflow 拼接、Gradle 侧没有 outputFileName 定制。
    它只用于最后那条断言：显示名必须是「原名 + suffix」且与产物名前缀一致，否则同一版本在
    Release 列表里的文件名与手机上的应用名对不上。
    """
    return [
        # ═══════════════════════ PROJECT-CUSTOM-BEGIN ═══════════════════════
        # 只改 applicationId（最终包名），不动 namespace：R 类、资源引用、类的全限定名都跟
        #   namespace 走，改它会让 manifest 里的 `.ui.MainActivity` 解析到不存在的类（能装、一开就崩）。
        #   代码里对自身包名的判断全部走 BuildConfig.APPLICATION_ID（HookInit / ContextAmbient），
        #   改这里即自动跟随。
        (BUILD_GRADLE, "        applicationId = namespace", f'        applicationId = "{app_id}"'),
        # 显示名：launcher、LSPosed 模块列表、系统设置里的应用名都读这个。只**追加** fork 后缀
        #   （Guise → Guise.F），不换名字 —— 换了等于让人分不清这还是不是原来那个模块。
        #   本工程 app_name 是 translatable="false"，只在 values/ 有一份，没有 locale 副本要同改。
        (
            APP_NAME_XML,
            '<string name="app_name" translatable="false">Guise</string>',
            f'<string name="app_name" translatable="false">Guise{suffix}</string>',
        ),
        # 应用内更新源：不指向 fork 的话，fork 包会拿着上游最新版的元数据去比版本、点「更新」还会
        #   下载上游 APK（包名/签名都不同，装必失败）。四处 URL 全部指向 fork，配套的
        #   latest-*.json 也放在 fork 的 main 上。
        (
            APP_UPDATER,
            f'const val RELEASES_URL = "https://github.com/{UPSTREAM_REPOSITORY}/releases"',
            f'const val RELEASES_URL = "https://github.com/{FORK_REPOSITORY}/releases"',
        ),
        (
            APP_UPDATER,
            f'private const val MANIFEST_REPOSITORY_PATH = "{UPSTREAM_REPOSITORY}@main"',
            f'private const val MANIFEST_REPOSITORY_PATH = "{FORK_REPOSITORY}@main"',
        ),
        (
            APP_UPDATER,
            f'"https://api.github.com/repos/{UPSTREAM_REPOSITORY}/contents/$manifestName?ref=main",',
            f'"https://api.github.com/repos/{FORK_REPOSITORY}/contents/$manifestName?ref=main",',
        ),
        (
            APP_UPDATER,
            f'"https://raw.githubusercontent.com/{UPSTREAM_REPOSITORY}/main/$manifestName",',
            f'"https://raw.githubusercontent.com/{FORK_REPOSITORY}/main/$manifestName",',
        ),
        # ════════════════════════ PROJECT-CUSTOM-END ════════════════════════
    ]


# 改写完成后逐条校验：新写法必须恰好 1 处、旧写法必须不再出现。
#   旧写法是新写法的子串时（包名 …guise → …guise.fork）跳过子串比较，否则必然误报残留。
def verify_edits(edits: list[tuple[str, str, str]]) -> list[str]:
    hits: list[str] = []
    for rel, old, new in edits:
        text = (REPO_ROOT / rel).read_text(encoding="utf-8")
        got = text.count(new)
        if got != 1:
            hits.append(f"{rel}: 改写后写法出现 {got} 处（应 1 处）")
        if old not in new and old in text:
            hits.append(f"{rel}: 仍残留旧写法: {old.splitlines()[0][:80]}")
    return hits


def validate(app_id: str, label: str, suffix: str) -> list[str]:
    if not re.fullmatch(r"[A-Za-z0-9._]+", app_id):
        return [f"--app-id 不合法：{app_id!r}"]
    if not re.fullmatch(r"[A-Za-z0-9._-]+", label):
        return [f"--label 只允许 A-Za-z0-9._-（它进 APK 文件名与下载 URL）：{label!r}"]
    if not re.fullmatch(r"[A-Za-z0-9._-]+", suffix):
        return [f"--label-suffix 只允许 A-Za-z0-9._-：{suffix!r}"]
    if label != f"Guise{suffix}":
        return [f"--label 与显示名不同源：显示名会是 Guise{suffix}，产物名前缀却是 {label!r}"]
    return []


def apply(edits: list[tuple[str, str, str]]) -> list[str]:
    problems: list[str] = []
    for rel, old, _new in edits:
        path = REPO_ROOT / rel
        if not path.is_file():
            problems.append(f"{rel}: 文件不存在")
            continue
        got = path.read_text(encoding="utf-8").count(old)
        if got != 1:
            problems.append(f"{rel}: 期望 1 处、实际 {got} 处: {old}")
    if problems:
        return problems
    for rel, old, new in edits:
        path = REPO_ROOT / rel
        path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
        print(f"  {rel}: {old} → {new}")
    return verify_edits(edits)


def selftest() -> int:
    """不联网、不碰仓库：用临时目录造原文，验改写链路与参数闸门。"""
    import tempfile

    global REPO_ROOT
    fails: list[str] = []

    for args, want_ok in (
        (("com.houvven.guise.fork", "Guise.F", ".F"), True),
        (("com.houvven.guise.fork", "Guise.F", ".F "), False),
        (("com.houvven.guise.fork", "Guise.Reborn", ".F"), False),
        (("bad-app-id", "Guise.F", ".F"), False),
    ):
        got_ok = not validate(*args)
        if got_ok != want_ok:
            fails.append(f"validate{args} 期望 {'通过' if want_ok else '拒绝'}，实际相反")

    orig_root = REPO_ROOT
    with tempfile.TemporaryDirectory() as tmp:
        REPO_ROOT = Path(tmp)
        try:
            edits = build_edits("com.houvven.guise.fork", "Guise.F", ".F")
            by_file: dict[str, list[str]] = {}
            for rel, old, _new in edits:
                by_file.setdefault(rel, []).append(old)
            for rel, olds in by_file.items():
                path = REPO_ROOT / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("\n".join(olds), encoding="utf-8")
            problems = apply(edits)
            if problems:
                fails.append(f"改写链路报错：{problems[:2]}")
            # 显示名必须是「原名 + 后缀」，不是被替换成产物名前缀
            xml = (REPO_ROOT / APP_NAME_XML).read_text(encoding="utf-8")
            if ">Guise.F<" not in xml:
                fails.append("显示名没有按「原名 + 后缀」改写")
            # 更新源必须整体指向 fork，不能残留上游路径
            updater = (REPO_ROOT / APP_UPDATER).read_text(encoding="utf-8")
            if UPSTREAM_REPOSITORY in updater:
                fails.append("更新源仍残留上游仓库路径")
            # 原文缺失必须整体失败（上游改了写法时的行为）
            (REPO_ROOT / BUILD_GRADLE).write_text("something else\n", encoding="utf-8")
            if not apply(edits):
                fails.append("原文缺失时没有失败")
        finally:
            REPO_ROOT = orig_root

    for f in fails:
        print(f"::error::selftest 失败：{f}", file=sys.stderr)
    print(f"selftest {'通过' if not fails else '失败'}（{len(fails)} 项）")
    return 0 if not fails else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--app-id", default=DEFAULT_APP_ID)
    parser.add_argument("--label", default=DEFAULT_LABEL)
    parser.add_argument("--label-suffix", default=DEFAULT_LABEL_SUFFIX)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()

    invalid = validate(args.app_id, args.label, args.label_suffix)
    if invalid:
        for msg in invalid:
            print(f"::error::{msg}", file=sys.stderr)
        return 1

    if args.app_id == UPSTREAM_APP_ID:
        print(f"::error::--app-id 必须与上游包名 {UPSTREAM_APP_ID} 不同（否则装不上/顶掉上游）",
              file=sys.stderr)
        return 1

    edits = build_edits(args.app_id, args.label, args.label_suffix)

    if args.dry_run:
        for rel, old, new in edits:
            print(f"[dry-run] {rel}\n    - {old}\n    + {new}")
        return 0

    hits = apply(edits)
    if hits:
        print("::error::fork 身份改写未通过：", file=sys.stderr)
        for h in hits:
            print(f"  - {h}", file=sys.stderr)
        return 1

    print(f"已改写为 fork 身份：appId={args.app_id} 产物名前缀={args.label}"
          f" 显示名=Guise{args.label_suffix}（共 {len(edits)} 项，仅工作区，不入库）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
