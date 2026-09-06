#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把手機戰情板頁首改成 Shadow Desk ＋ 吉祥物 logo，直接改在產生 HTML 的腳本上。

用法（在放著 報表.html / 看報表.bat 的資料夾）：
    python patch_shadow_desk.py            # 掃描這個資料夾與子資料夾，直接套用
    python patch_shadow_desk.py D:\\某個資料夾  # 指定資料夾
    python patch_shadow_desk.py --dry-run  # 只看會改哪些檔案，不動手

改之前每個檔案都會先備份成 檔名.bak-年月日-時分秒，改壞了把備份改回原名就好。
重複執行不會重複貼（偵測到已經有 class='brand' 就跳過）。
"""

import argparse
import datetime
import pathlib
import sys

# ── 要找的錨點 ────────────────────────────────────────────────────────────────
OLD_TITLE = "<title>影子模式戰情板</title>"
NEW_TITLE = "<title>Shadow Desk</title>"
OLD_H1 = "<h1>影子模式戰情板</h1>"

# ── 要貼進去的品牌區塊 ────────────────────────────────────────────────────────
# 自帶 <style>，所以不用去動原本那一大段 CSS，只換這一行 <h1>。
# 屬性一律用單引號、CSS 字體名不加引號，避免撞到 Python 字串的雙引號。
BRAND_BLOCK = """<style>
.brand{display:flex;align-items:center;gap:13px;}
.brand .mark{flex:none;width:46px;height:46px;display:block;filter:drop-shadow(0 3px 8px rgba(217,103,74,.3));}
.brand h1{font-family:IBM Plex Mono,ui-monospace,SFMono-Regular,monospace;font-size:1.42rem;font-weight:600;letter-spacing:-.005em;margin:0;line-height:1.15;}
.brand .sub{margin:3px 0 0;font-size:.76rem;color:var(--text-3);letter-spacing:.06em;}
@media (max-width:360px){.brand .mark{width:40px;height:40px;}.brand h1{font-size:1.26rem;}}
</style>
<div class='brand'>
<svg class='mark' viewBox='0 0 48 48' role='img' aria-label='Shadow Desk'>
<defs>
<linearGradient id='sdSkin' x1='10' y1='4' x2='38' y2='46' gradientUnits='userSpaceOnUse'>
<stop offset='0' stop-color='#FFC98F'/><stop offset='.52' stop-color='#F2955F'/><stop offset='1' stop-color='#D9674A'/>
</linearGradient>
<linearGradient id='sdLens' x1='10' y1='20' x2='38' y2='31' gradientUnits='userSpaceOnUse'>
<stop offset='0' stop-color='#2C3444'/><stop offset='1' stop-color='#10141A'/>
</linearGradient>
</defs>
<circle cx='13' cy='9.2' r='5.1' fill='url(#sdSkin)'/>
<circle cx='35' cy='9.2' r='5.1' fill='url(#sdSkin)'/>
<rect x='5.5' y='8.5' width='37' height='33' rx='13.5' fill='url(#sdSkin)'/>
<rect x='7.2' y='22.1' width='4.6' height='2.7' rx='1.35' fill='url(#sdLens)'/>
<rect x='36.2' y='22.1' width='4.6' height='2.7' rx='1.35' fill='url(#sdLens)'/>
<rect x='21.4' y='23.2' width='5.2' height='2.5' rx='1.25' fill='url(#sdLens)'/>
<rect x='9.8' y='20.4' width='12.6' height='9' rx='4.4' fill='url(#sdLens)'/>
<rect x='25.6' y='20.4' width='12.6' height='9' rx='4.4' fill='url(#sdLens)'/>
<path d='M13.2 27.4 L16.4 22.8' stroke='#fff' stroke-opacity='.38' stroke-width='1.7' stroke-linecap='round'/>
<path d='M29 27.4 L32.2 22.8' stroke='#fff' stroke-opacity='.38' stroke-width='1.7' stroke-linecap='round'/>
<path d='M20.6 34.4 q3.4 2.9 6.8 0' fill='none' stroke='#A8452A' stroke-opacity='.6' stroke-width='1.9' stroke-linecap='round'/>
</svg>
<div><h1>Shadow Desk</h1><p class='sub'>影子模式戰情板</p></div>
</div>"""

SCAN_SUFFIXES = {".py", ".pyw", ".html", ".htm", ".js", ".ts", ".txt", ".tpl", ".jinja", ".j2"}
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", "env", ".idea", ".vscode"}
ENCODINGS = ("utf-8-sig", "utf-8", "cp950", "big5")


def read_text(path):
    """回傳 (內容, 編碼)；讀不出來就回 (None, None)。"""
    raw = path.read_bytes()
    for enc in ENCODINGS:
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return None, None


def needs_doubled_braces(text):
    """f-string / str.format 樣板裡的 CSS 大括號會寫成 {{ }}，插入的 CSS 也要跟著加倍。"""
    return ".head{{" in text or "text-wrap:balance;}}" in text or ".badge{{" in text


def double_braces(block):
    return block.replace("{", "{{").replace("}", "}}")


def patch_text(text):
    """回傳 (新內容, 這次做了哪些事)。沒得改就回 (text, [])。"""
    done = []
    out = text

    if OLD_TITLE in out:
        out = out.replace(OLD_TITLE, NEW_TITLE)
        done.append("標題 → Shadow Desk")

    if OLD_H1 in out:
        block = double_braces(BRAND_BLOCK) if needs_doubled_braces(out) else BRAND_BLOCK
        out = out.replace(OLD_H1, block)
        done.append("頁首 → 吉祥物 logo")

    return out, done


def main():
    ap = argparse.ArgumentParser(description="把戰情板頁首永久換成 Shadow Desk ＋ 吉祥物 logo")
    ap.add_argument("folder", nargs="?", default=".", help="要掃描的資料夾（預設：目前資料夾）")
    ap.add_argument("--dry-run", action="store_true", help="只列出會改什麼，不真的動檔案")
    args = ap.parse_args()

    root = pathlib.Path(args.folder).expanduser().resolve()
    if not root.is_dir():
        print("找不到資料夾：%s" % root)
        return 2

    print("掃描：%s" % root)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    patched, already, mentions = [], [], []

    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SCAN_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if ".bak-" in path.name:
            continue

        text, enc = read_text(path)
        if text is None or "影子模式戰情板" not in text:
            continue

        if "class='brand'" in text or 'class="brand"' in text:
            already.append(path)
            continue

        new_text, done = patch_text(text)
        if not done:
            mentions.append(path)  # 有提到名字但找不到錨點，要人工看
            continue

        if args.dry_run:
            print("  [預覽] %s：%s" % (path.relative_to(root), "、".join(done)))
        else:
            backup = path.with_name(path.name + ".bak-" + stamp)
            backup.write_bytes(path.read_bytes())
            path.write_text(new_text, encoding=enc)
            print("  [已改] %s：%s（備份 %s）" % (path.relative_to(root), "、".join(done), backup.name))
        patched.append(path)

    print("")
    if patched:
        if args.dry_run:
            print("預覽：會改 %d 個檔案（這次沒有動到任何檔案）。" % len(patched))
        else:
            print("改好 %d 個檔案。" % len(patched))
            print("接下來：重跑一次產生報表的腳本（或等下一次自動更新），頁面就會是新的樣子。")
    if already:
        print("已經是新版、跳過：%d 個檔案。" % len(already))
    if mentions:
        print("")
        print("這些檔案有提到「影子模式戰情板」，但找不到 <h1>影子模式戰情板</h1> 這個錨點，沒有動它：")
        for p in mentions:
            print("  - %s" % p.relative_to(root))
        print("把上面的檔案內容貼給 Claude，我直接幫你改。")
    if not patched and not already and not mentions:
        print("這個資料夾裡沒有找到產生戰情板的檔案。")
        print("請改成：python patch_shadow_desk.py 放著 報表.html 跟 看報表.bat 的資料夾路徑")
    return 0


if __name__ == "__main__":
    sys.exit(main())
