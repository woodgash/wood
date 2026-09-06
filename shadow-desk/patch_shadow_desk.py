#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把手機戰情板改成 Shadow Desk：頁首吉祥物 logo ＋ 手機桌面 App 圖示。
直接改在產生 HTML 的腳本上，所以每天自動重新產生也不會掉。

用法（在放著 報表.html / 看報表.bat 的資料夾）：
    python patch_shadow_desk.py            # 掃描這個資料夾與子資料夾，直接套用
    python patch_shadow_desk.py D:\\某個資料夾  # 指定資料夾
    python patch_shadow_desk.py --dry-run  # 只看會改哪些檔案，不動手

改之前每個檔案都會先備份成 檔名.bak-年月日-時分秒，改壞了把備份改回原名就好。
重複執行不會重複貼；已經有頁首、只缺 App 圖示的檔案，會只補圖示那一段。
"""

import argparse
import datetime
import pathlib
import sys

# ── 要找的錨點 ────────────────────────────────────────────────────────────────
OLD_TITLE = "<title>影子模式戰情板</title>"
NEW_TITLE = "<title>Shadow Desk</title>"
OLD_H1 = "<h1>影子模式戰情板</h1>"

# ── 1. 頁首品牌區塊 ───────────────────────────────────────────────────────────
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
<stop offset='0' stop-color='#2C3444'/><stop offset='1' stop-color='#141A24'/>
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

# ── 2. 手機桌面 App 圖示 ──────────────────────────────────────────────────────
# iOS 加到主畫面時讀 apple-touch-icon；圖直接用 base64 內嵌，不依賴任何外部檔案。
# base64 裡沒有大括號，所以放進 f-string 樣板也不用跳脫。
ICON_180_B64 = """
iVBORw0KGgoAAAANSUhEUgAAALQAAAC0CAMAAAAKE/YAAAABgFBMVEX///////7+/////v7//f3+/f38+fj06OPq0cbtso/yr4bz
r4Pwr4j0roDzroL1rn3zrX/0rXzxroXyrYLxrILxq3/yqnzwqoHwqX7xqHvvqH/vp3zwpnnvpXnvo3bupn7upHrtonjtoHbtoHPs
nnPtnW/rnHDsm23rmmzrl2jqm3Hql2vqlmjplGXpkWLokmXWlnnoj2DnjV3mjWDmilvlilzlh1fkh1njhVfkhFTihFjjg1LjgVDi
glbigVPigFHif0/hf1Difk7hfU7hfE3gf1TffVDffE/fe03fek3feUzeeEvdeE3eeErdd0vddkrcd07cdUrbdEnbc0jackjacUfX
el19gorZcEfZb0bYb0bYbkbXbkfXbUXXbEXWbEXXa0XWa0XWa0TWakTVakTVaUPVaELUaUPUaEPUaELUZ0LTZkLTZULTZUDSZUHS
ZEDRY0DRYkDQYT/PYD/OXj7NXT3MWz2MV04pM0QlLj4jLDshKTcdJDEZICwXHikSGSWFcjPRAAAbs0lEQVR42sWdi0MTx/bHlxuS
bBQshiAIyksUBTTyiCheEIrIQwUUlLdUFOu9XqS1tfLmX/+dc+Z1ZnY2wVb4nZA0Urd8+PY735ndnZkEF6F+gi8oehFVpd5UVlVW
VVXCU1WNeNRcqrmEX5cu19VdxrpCdRWrUdQ1WW3XqdqhbmJ1dt661XWr67aoO1jdWD1YfVT3RD2Aegj1b1nD/x6G+nk4IGh/AWwl
AhM4w9YF1IAsoBsaNLUDLanbFTUw3+rqktD5O4q6h0H3G2oOLZh//jkgZg92ZdVPlQKanhK8xoJGbkOthC4CrZU21FrpnpJKk8o/
K2gPdmXlT0JlWX6pkfqS8AdT2qFua0PqG6Wgu6NK29DDUmeE/omgHerKnyrtkrwXXOaaOoAm7IaGBge6NQLdTswcOq+Zo55+IKFd
ZoKOmKMyUkB7ASqCjNSIbKiNq1tbNTVC31CWRuquokpLoe9LoR9qZoIeVUpb6VHp6nyhqlIgX6iGylVVu9TaIFcJutGCbrumoRU1
Sc0aoob2uuMha4MIPUpK21pHZBYqQ1XLqopA19U1UEl/tHB7KKVvMHt0eezRW8TSGHY/K2aAdg0dsbMEpmc1vuSqc7lcTc6mJns0
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
"""

ICON_64_B64 = """
iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAMAAACdt4HsAAABIFBMVEX///////7+/////v7//v3//f3+/v79/f39/Pv29PP05+Hp
zsLytI7yr4XitZ7zroH1rn70rX7zrH3xroXyrYLxrIHxq4Dxqn3wqoDwqHzwpnnvo3bupXztonftoHTtnnLsnXDsm27rmmzrl2nq
mnDqlWjpk2Tok2bPmYXnj2Pnjl7ni1zli17liFrlh1jkhlfjhVbkg1LjgVDiglTigFHifk7hf1DhfU3gf1TgfE7fekzeek/eeUvd
eE3ddkrcd03bdEnbc0jackiWgIDZcEbYb0fYbkbXbUfXbEXWa0TWakTVakTVaULUaEPUZ0PTZ0LTZkLSZUHTZD/RY0DRYkDQYT/P
YD/OXj7MXD2YXVI+RlMrM0IjLDwdJTMZIC0SGSUaHXRpAAAGg0lEQVR42o2Xi1biSBCG2w2X0HHY0QgCgoDKTUFQEbk4gAYEFF1l
dxxPAPP+b7FV1Z0LjKv76+FwcvJ/demkumHfvdpCRaO7oHg8kUjs7e3t76fTmWz24PAwl8vn86Xj45OTymm1dnZ2fn5+eXnJPPY/
hSIRQiBhby/1/wHSvrMjCTKFfSBkMgQogH8FAP4rtuYHwA4CohKQ8gByawD0X7Htra2V+CgCACEJgNR/ZlAXgC0CSPu3HZsQixEg
4QAOAFBAQFkALup1sF+1BED4v6F0kCAAICkB2RVApXJaq50RoNUGwPet765fIAgQcwFHAMjZgHKlAglc1BsAaLexB1tb6wAgCEDy
Q8CpAFy1VgA737yENcARVACA0gqg1W63r9n29jpAXwOkJaBAAKwAWgA9RMA1Aba3aAF1CdhEBgKSXgDUQAQBoBa0wI8AQND6S8Cm
jsFjugdwBModH5crJwLgVHB93fUCdLLrYY1zbTNJgBQC0J9PhzVNi1XKq4Bul+0iIRohABD0Tc5QIS0Zs3sI/kI4RJe1QqVcqVYv
LpoIAD8Adrd3d6MRSUC/4gPBvSknhXQhzJjP7/MrjJdEAs1Go3UtAaAoECII2NWYn0Ipiqpn00f0BOZKSVVR6LLKtLoEtDrg7/dZ
XBIwCT2yqYobgcC45gjSElc3FLVQA0ATAD9+gL/PEg4hGtHjYbbBPpXC9Aa2oNnq/MAEblgiEUdELAp/ekLbUNx7fbb87kWfstmq
YgKdDiUgAIiAxY9FkmGmfJVBrFGjBDo9TAABAhGP4/Ojhz6vQWGhEhbQ7FAFNze3BLAR8dg+Z77PAH6mtTGBDiUA/lu2JwgJWPN4
POWuwseCVUi2CPCj1wf77YDB6E/sSUIyyb/qgY9xKgBbiP4hAkhISGufFyAIm10ngcFg4ABg/qZSfEP5CqAovCM6QP47BnNfulPp
TeVLPxKO+p1eT/rvWHpfKpXKygoCQl6X55KfhQedXr8P/uHwbszSLuGA1jBoOwNB2x60vwVUWkkEYALgH7NMmoSEDGd+dIeEwCj9
nkss4Ge8LxMAPwAymbSEZDjYlaIJmuOHxiiZAAub8/l8sZjPTQOaFODYAbCjf8KyGUdZDpGM5QJkwv3LdwOCb6jMsKz3d2u+sEAm
55ABJiD89yzr6CjDDdNcYDDTMBBjQQ4Q31oul+9zw3gHWYulyXu3t9i/8WRy/8AOpLLZw0RxOZ9Lv4mApUnlvIN/CZcsIliWUb0j
P8R/mDoAmF1pjeLPIZhJhUAVKEzANEz6bkEOWntIDZgQ4NAWDD/ODU8BAkF6x0sCYBmcQwIy/vTRBcAJApoo/HPpNnEgQmjIaW7J
DEKM3905/ieWc1XiwaDxbjcAls0ycBkNa2E3AABmMKhNKf+H6ePj0zODk1ced71cIXei/RHg5gL8IgPLDKnBoBoyLWiAaIc15/Ak
zoYUH/x/CQCqkC+chGHuQxtE3cuFEcInKcDg2bCkTA63xGYj6X96dgGlfOE4paKDO5uB/SR6L/mZ2pyOZf7Pzy+shMrTZ6kCb5P7
CjHVLweh6lwKBrCC0YT69xf4X9ixEAFOdXodpcirKH7xPqqoIGZwNBvL+l9eXv62AahyqWpvjbS1FTXxVSu6o5IS8Pi9gBPY+gsh
eyrCnaNmUQuFtGJz5HD9LNSbSv8z+v9hJ67KlfIZ9FHeq/i1cq9ZKjV7Zc2n2H61NBtD/Y+2XwIq8E8q15Mh5myFPFwsl4thblcF
8QuzkdM/9P9k4DoV5sopqHIJDzQcJpQNjMdUzmmKwSj1w6fWBL9bP/hf2amtKqhWq1UbF/KUIzxg98thzfXpqv/nz9dXVq0KL5pB
F6Drmq5xdXWYq1xLDWeTMfgfPfFff7Ga1Jkwg5oXjW63WT6yVcDzYXM4m92P7r31Y3wAnNkicx0OoCDY/bo3NwPcOcaTKWkycp6/
F4/fAZyf1+vS3Wq1cPOC7Q+mL4xPmH/D0ch9/zz5//r1xshM9oZ0t/AECccHPICI7cOeH576Zfw3BJyLn1+X9AOETuB0AOyK/X8g
56f9/q35AXAuAWCH4z/5KTqdP2j/vLPjPz2t9A/9b8zj90b3+J355z6/wu8C3PgeP50/Bqv5/xafAJcf+G/W4z/+tn5vNmDVfy3T
d/s/kfP7eW39bIDs/wf1D+349Pw9rdb/5gVciQR+65+9/z2svL+rfgSs1L+WP/VvLf8V/9u/slqVHtBQ+bwAAAAASUVORK5CYII=
"""


def icon_links():
    i180 = "".join(ICON_180_B64.split())
    i64 = "".join(ICON_64_B64.split())
    return (
        "<link rel='apple-touch-icon' sizes='180x180' href='data:image/png;base64,%s'>\n"
        "<link rel='icon' type='image/png' sizes='64x64' href='data:image/png;base64,%s'>" % (i180, i64)
    )


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


def has_brand(text):
    return "class='brand'" in text or 'class="brand"' in text


def patch_text(text):
    """回傳 (新內容, 這次做了哪些事)。沒得改就回 (text, [])。"""
    done = []
    out = text

    if OLD_TITLE in out:
        out = out.replace(OLD_TITLE, NEW_TITLE)
        done.append("標題 → Shadow Desk")

    if OLD_H1 in out and not has_brand(out):
        block = double_braces(BRAND_BLOCK) if needs_doubled_braces(out) else BRAND_BLOCK
        out = out.replace(OLD_H1, block)
        done.append("頁首 → 吉祥物 logo")

    # App 圖示：接在 <title> 後面。只有本來就有 <title> 的樣板才補，避免貼到奇怪的地方。
    if "apple-touch-icon" not in out and NEW_TITLE in out:
        out = out.replace(NEW_TITLE, NEW_TITLE + "\n" + icon_links(), 1)
        done.append("桌面圖示 → 內嵌 App icon")

    return out, done


def main():
    ap = argparse.ArgumentParser(description="把戰情板永久換成 Shadow Desk 的 logo 與 App 圖示")
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
        if text is None:
            continue
        if "影子模式戰情板" not in text and "Shadow Desk" not in text:
            continue

        new_text, done = patch_text(text)
        if not done:
            if has_brand(text) and "apple-touch-icon" in text:
                already.append(path)
            elif "影子模式戰情板" in text:
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
            print("接下來：重跑一次產生報表的腳本（或等下一次自動更新）。")
            print("手機那邊：桌面圖示是加到主畫面當下就被 iOS 存起來的，不會自己換 ——")
            print("把舊捷徑長按刪掉，重新開頁面再「加入主畫面」一次，才會看到新圖示。")
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
