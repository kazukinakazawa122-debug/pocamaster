"""@_pipipup の「IVE MD pc List. 02」（メンバーごと 6 枚、2026-10-01 に本人が追加。pocamaster-images/新しい資料 2026-10-01/MD List 02・ソロ契約_pipipup/）

- 6 人とも同じ並び（段 r・左から c）。ユジンの表の位置を基準に、ほかの 5 人は画像の横の位置（割合）で同じカードを探す
- カードに ID はないが、一部のカードに「@BEAPCTRADING ON IG」など別の人の ID の透かしが写っている → WATERMARK に書いた位置は画像なし（本人のルール）
- すでに画像のある枠は、新しい画像が 1.25 倍以上大きいときだけ差し替える。画像のない枠は埋める
- 新しい枠：SHOW WHAT I HAVE の SuperStar Tokyo 2 種、in CINEMA Taiwan
"""
import csv, glob, json, os, sys
from PIL import Image
import grid
from build2 import *

D = ROOT + "新しい資料 2026-10-01/MD List 02・ソロ契約_pipipup/"
NAMES = ["ユジン", "ガウル", "レイ", "ウォニョン", "リズ", "イソ"]


def table(n):
    """メンバー n の表のカードを、段（上から）・左から順に並べて返す"""
    im = grid.load(D + f"MD List 02_{n}.png")
    bs = sorted(grid.card_boxes(im, min_w=0.02, max_w=0.08), key=lambda b: (b[1] + b[3]) / 2)
    rows = []
    for b in bs:
        cy = (b[1] + b[3]) / 2
        if rows and abs(cy - rows[-1][0]) < 150:
            rows[-1][1].append(b)
        else:
            rows.append([cy, [b]])
    return im, [sorted(r[1], key=lambda b: b[0]) for r in rows]


CREDIT = "@_pipipup"
PROM = "1st FAN CONCERT 'The Prom Queens'"
MAG = "2nd FANMEETING 'MAGAZINE IVE'"
SWIH = "1st WORLD TOUR 'SHOW WHAT I HAVE'"
ENC = "Encore（アンコール）"
DVD = "DVD・Blu-ray・Kit"
COLLAB = "Collab & Event｜コラボ・イベント"
FC = "DIVE Official Fanclub｜ファンクラブ"
PB = "1st PHOTOBOOK 'A Dreamy Day'"
# (段, 列, コレクション, 入手元, バージョン)  ラベルは表のカードの下の文字（2026-10-01 に目で読んだ）
MAP = [
    (3, 15, PROM, DVD, "DVD"), (3, 16, PROM, DVD, "Kit"), (3, 17, PROM, DVD, "Kit POLA"), (3, 18, PROM, DVD, "Blu-ray"),
    (3, 19, PROM, DVD, "Starship Square 特典"), (3, 20, PROM, DVD, "特典（店舗不明）"), (3, 21, PROM, DVD, "Apple Music 特典"),
    (5, 1, MAG, "Random Photocard Pack", "1"), (5, 2, MAG, "Random Photocard Pack", "2"),
    (5, 3, MAG, "Random Photocard Pack", "3"), (5, 4, MAG, "Random Photocard Pack", "4"),
    (5, 10, MAG, "MD", "Polaroid"), (5, 11, MAG, "MD", "Photo Kit"), (5, 12, MAG, "MD", "Photocard Holder"),
    (5, 13, MAG, "MD", "Acrylic Turning Stand"), (4, 22, MAG, "Special Photocard", "Day 1"), (5, 0, MAG, "Special Photocard", "Day 2"),
    (7, 11, MAG, "SuperStar STARSHIP", "1"), (7, 12, MAG, "SuperStar STARSHIP", "2"),
    (7, 13, MAG, "SuperStar STARSHIP", "3"), (7, 14, MAG, "SuperStar STARSHIP", "4"),
    (4, 15, SWIH, "DIVE JAPAN", "Label Drink"), (4, 18, SWIH, "Thailand Random Photocard", "1"), (4, 19, SWIH, "Thailand Random Photocard", "2"),
    (4, 20, SWIH, "MD", "Trading Card Stand（東京ドーム）1"), (4, 21, SWIH, "MD", "Trading Card Stand（東京ドーム）2"),
    (5, 15, SWIH, ENC, "DIVE ZONE Day 1"), (5, 16, SWIH, ENC, "DIVE ZONE Day 2"), (5, 19, SWIH, ENC, "Wing Hair Pin Set"),
    (5, 20, SWIH, ENC, "Photocard Holder Keyring"), (5, 21, SWIH, ENC, "Compact Mirror"),
    (7, 15, SWIH, ENC, "SuperStar STARSHIP 1"), (7, 16, SWIH, ENC, "SuperStar STARSHIP 2"),
    (1, 10, COLLAB, PB, "Pool Party ver."), (1, 11, COLLAB, PB, "Summer Beach Story ver."), (1, 12, COLLAB, PB, "Polaroid"),
    (1, 13, COLLAB, PB, "Starship Square"), (1, 14, COLLAB, PB, "withmuu"),
    (0, 4, FC, "DIVE JAPAN Phone Tab", "FC 特典"), (0, 5, FC, "DIVE 3期 'IVE SCOUT'", ""), (0, 6, FC, "DIVE 3期 'IVE SCOUT'", "DIVE JAPAN"),
    # 新しい枠
    (7, 9, SWIH, "SuperStar STARSHIP", "Tokyo (Baddie)"), (7, 10, SWIH, "SuperStar STARSHIP", "Tokyo (Off The Record)"),
    (6, 14, SWIH, "in CINEMA", "Taiwan"),
]
NEW = {(SWIH, "SuperStar STARSHIP", "Tokyo (Baddie)"), (SWIH, "SuperStar STARSHIP", "Tokyo (Off The Record)"), (SWIH, "in CINEMA", "Taiwan")}
WATERMARK = set()  # (段, 列) または (メンバー, 段, 列)。目で見て別の人の ID の透かしがあった位置（あとで埋める）
if os.path.exists(SP + "pp_watermark.json"):
    WATERMARK = {tuple(x) for x in json.load(open(SP + "pp_watermark.json"))}


def seed_keys():
    rows = csv.DictReader(open(PROJ + "public/seed/cards.csv", encoding="utf-8"))
    return {(r["collection"], r["member"], r["source"], r["version"]) for r in rows}


def cur_images():
    cur = {}
    for p in sorted(glob.glob(SP + "out/*.json")):
        b = os.path.basename(p)
        if b.startswith("_") or b.startswith("pipipup"):
            continue
        for e in json.load(open(p, encoding="utf-8"))["images"]:
            cur[(e["collection"], tuple(e["members"]), e["source"], e["version"])] = e
    return cur


def align(tabs):
    """ユジンの表の位置に、ほかの人の表のカードを横の位置の割合で合わせる"""
    im0, rows0 = tabs["ユジン"]
    out = {}
    for n, (im, rows) in tabs.items():
        for r, row0 in enumerate(rows0):
            for c, b0 in enumerate(row0):
                x0 = (b0[0] + b0[2]) / 2 / im0.width
                if r >= len(rows):
                    continue
                best = min(rows[r], key=lambda b: abs((b[0] + b[2]) / 2 / im.width - x0))
                if abs((best[0] + best[2]) / 2 / im.width - x0) < 0.012:
                    out[(n, r, c)] = (im, best)
    return out


if __name__ == "__main__":
    tabs = {n: table(n) for n in NAMES}
    al = align(tabs)
    have, cur = seed_keys(), cur_images()
    j = Job("pipipup_md02")
    stat = {"new": 0, "fill": 0, "bigger": 0, "keep": 0, "wm": 0, "noslot": 0, "nocard": 0}
    for n in NAMES:
        for r, c, coll, src, ver in MAP:
            if (n, r, c) not in al:
                stat["nocard"] += 1; print("見つからない", n, r, c); continue
            if (r, c) in WATERMARK or (n, r, c) in WATERMARK:
                stat["wm"] += 1; continue
            im, b = al[(n, r, c)]
            crop = im.crop(inset_frame(im, b))
            key = (coll, (n,), src, ver)
            is_new = (coll, src, ver) in NEW
            if not is_new and (coll, n, src, ver) not in have:
                stat["noslot"] += 1; print("枠がない", n, coll[:12], src, ver); continue
            old = cur.get(key)
            if old is None:
                stat["new" if is_new else "fill"] += 1
            else:
                ow = min(Image.open(CARDS + old["file"]).size)
                if min(crop.size) < ow * 1.25:
                    stat["keep"] += 1; continue
                stat["bigger"] += 1
            j.add(coll, [n], src, ver, crop, CREDIT)
    j.save()
    print(stat)
