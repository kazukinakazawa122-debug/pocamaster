"""イソのノンアルバムのページ（leeseo_na.jpg）で「ない」とされたカードのうち、アプリにすでに画像のある枠の見比べページを作る
出力：public/_review/leeseo_na_have.html（Git には入れない）。「ちがう」＝表の画像のほうが正しい（枠の画像を入れ替える）"""
import base64, csv, glob, io, json, os
import grid
from build2 import *

D = ROOT + "_nonalbum/idalshiro/"
OUT = PROJ + "public/_review/leeseo_na_have.html"
PARK, SCHOOL, PROM, SWIH, MAG = "MINIVE POP-UP 'MINIVE PARK'", "MINIVE POP-UP 'MINIVE SCHOOL'", "The Prom Queens", "SHOW WHAT I HAVE", "MAGAZINE IVE'"
# 番号 → (コレクション（部分）, 入手元（前方一致）, バージョン, 表のラベル)
ITEMS = {
    4: ("A RAY OF SUNSHINE", "Synnara", "", "SSG SYNNARA"), 8: ("Collab", "V Coloring", "", "VCOLORING"),
    22: (PROM, "MD", "PVC Card Holder", "HOLDER"), 29: ("Collab", PARK, "Face Cushion", "FACE CUSHION"),
    30: ("Collab", PARK, "Mega Cushion", "XL CUSHION"), 32: ("Collab", PARK, "50K Benefit 1st week", "50K KRW week 1"),
    33: ("Collab", PARK, "50K Benefit 2nd week", "BENEFIT week 2"), 34: ("Collab", "SuperStar STARSHIP", "KCON LA", "KCON LA"),
    35: ("Collab", "SuperStar STARSHIP", "LONDON", "LONDON EVENT"), 40: (PROM, "DVD", "Starship Square 特典", "SSQ"),
    41: (PROM, "DVD", "Apple Music 特典", "APPMU"), 42: (PROM, "DVD", "特典（店舗不明）", "KTOWN"),
    49: ("Fanclub", "DIVE JAPAN Phone Tab", "", "PHONE TAB"), 50: ("Fanclub", "DIVE JAPAN Phone Tab", "FC 特典", "DIVE BENEFIT"),
    52: ("Fairy's Wish", "Soundwave", "", "SW"), 72: (SWIH, "DIVE JAPAN", "Label Drink", "JP DRINK"),
    87: (MAG, "MD", "Photo Kit", "PHOTOKIT"), 88: (MAG, "MD", "Polaroid", "POLA SET"), 89: (MAG, "MD", "Photocard Holder", "PC HOLDER"),
    90: (MAG, "MD", "Acrylic Turning Stand", "ACRYLIC STAND"), 91: (MAG, "Special Photocard", "Day 1", "DIVE BOOTH"), 92: (MAG, "Special Photocard", "Day 2", "DIVE BOOTH"),
    120: (SWIH, "Encore（", "Compact Mirror", "MIRROR"), 124: (SWIH, "Encore（", "Photocard Holder Keyring", "PC HOLDER"),
    134: (SWIH, "DVD", "Ktown4U 特典", "KTOWN"), 176: ("Collab", SCHOOL, "Fluffy Plush", "FLUFFY PLUSH"), 177: ("Collab", SCHOOL, "Hug Bag", "HUG BAG"),
    178: ("Collab", SCHOOL, "70K Benefit", "70K KRW"), 179: ("Collab", SCHOOL, "Shanghai MD 特典", "SHANGAI BENEFIT"),
    180: ("Collab", SCHOOL, "Taipei & Kaohsiung MD 特典", "TAIWAN BENEFIT"),
}


def b64(img, w=240):
    img = img.convert("RGB"); img.thumbnail((w, w * 2))
    f = io.BytesIO(); img.save(f, "JPEG", quality=80)
    return "data:image/jpeg;base64," + base64.b64encode(f.getvalue()).decode()


if __name__ == "__main__":
    miss = json.load(open(SP + "review/miss_na_leeseo.json", encoding="utf-8"))
    rows = [r for r in csv.DictReader(open(PROJ + "public/seed/cards.csv", encoding="utf-8")) if r["member"] == "イソ"]
    cur = {}
    for p in sorted(glob.glob(SP + "out/*.json")):
        for e in json.load(open(p, encoding="utf-8"))["images"]:
            if e["members"] == ["イソ"]:
                cur[(e["collection"], e["source"], e["version"])] = e
    im = grid.load(D + "leeseo_na.jpg")
    html = []
    for idx, (csub, ssub, ver, lab) in ITEMS.items():
        f = [r for r in rows if csub in r["collection"] and r["source"].startswith(ssub) and r["version"] == ver]
        if len(f) != 1:
            print("枠が見つからない/複数", idx, csub, ssub, ver, len(f)); continue
        r = f[0]; e = cur.get((r["collection"], r["source"], r["version"]))
        if e is None:
            print("画像なし", idx); continue
        new = im.crop(inset_frame(im, miss[idx][1])); old = Image.open(CARDS + e["file"])
        html.append(f'<div class="row" id="r{idx}"><div class="col"><img src="{b64(old)}">いまのアプリ（{old.size[0]}px）</div>'
                    f'<div class="col"><img src="{b64(new)}">表の画像（{new.size[0]}px）</div>'
                    f'<div class="col" style="width:150px;text-align:left">#{idx} 表のラベル：{lab}<br><b>{r["source"]}</b> {r["version"]}<br>{r["collection"][:28]}<br>出典：{e["credit"]}</div>'
                    f'<div class="btns"><button class="y" data-i="{idx}">同じ</button><button class="n" data-i="{idx}">ちがう</button></div></div>')
    page = open(PROJ + "public/_review/leeseo_have.html", encoding="utf-8").read()
    head = page[:page.index("<main>") + 6]
    tail = page[page.index("</main>"):]
    head = head.replace("画像の見比べ（イソ）", "画像の見比べ（イソ・ノンアルバム）")
    open(OUT, "w", encoding="utf-8").write(head + "".join(html) + tail)
    print(len(html))
