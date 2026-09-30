"""（albums_ida_na_leeseo.py のイソの対応を、ほかの 5 人にも当てはめる）
イソのノンアルバムのページ（@idalshiro の leeseo_na.jpg）で、本人が「ない」とした 148 枚のうち、
アプリに枠があって画像のない枠（イソ）に、ラベルを目で読んで入れる（2026-10-01）

- 番号は review/review_na_leeseo.json（= review/miss_na_leeseo.json の何番目か）
- 入れないもの：すでに画像のある枠（見比べが要る）、2 人以上のカード（相手を顔で決めることになる）、
  「@BEAPCTRADING」の透かしがある 1st PHOTOBOOK（本人のルール）、どの枠かはっきりしないもの
"""
import csv, glob, json, os
import grid
from build2 import *

D = ROOT + "_nonalbum/idalshiro/"
CREDIT = "@idalshiro"
PROM, SWIH, SCOUT, SWIA, DII = "The Prom Queens", "SHOW WHAT I HAVE", "IVE SCOUT'", "SHOW WHAT I AM", "DIVE into IVE'"
COLLAB, MAGZ, FC = "Collab", "Magazine", "Fanclub"
DICON = "DICON"
# 番号 → (コレクション（部分）, 入手元（前方一致）, バージョン)
MAP = {
    36: (PROM, "DVD", "DVD"), 37: (PROM, "DVD", "Blu-ray"), 38: (PROM, "DVD", "Kit"), 39: (PROM, "DVD", "Kit POLA"),
    107: (MAGZ, DICON, "Type A 1"), 108: (MAGZ, DICON, "Type A 2"), 109: (MAGZ, DICON, "Type A 3"),
    111: (MAGZ, DICON, "Lucky Card Set 1"), 112: (MAGZ, DICON, "Lucky Card Set 2"),
    113: (MAGZ, DICON, "Type B 1"), 114: (MAGZ, DICON, "Type B 2"), 115: (MAGZ, DICON, "Type B 3"),
    117: (MAGZ, DICON, "Kakao 特典 1"), 118: (MAGZ, DICON, "Kakao 特典 2"), 119: (MAGZ, DICON, "Double Sided"),
    123: (SWIH, "Encore（", "Wing Hair Pin Set"), 125: (SWIH, "Encore（", "DIVE ZONE Day 1"),
    153: (SCOUT, "Random Photocard Pack Japan", "1"), 154: (SCOUT, "Random Photocard Pack Japan", "2"),
    155: (SCOUT, "MD", "Photo Kit"), 156: (SCOUT, "MD", "Bandana"), 157: (SCOUT, "MD", "Acrylic Stand"),
    158: (SCOUT, "MD", "Whistle Necklace"), 159: (SCOUT, "MD", "Stainless Mug"), 161: (SCOUT, "DIVE ZONE", "Day 2"),
    162: (SCOUT, "Lotte Cinema", ""), 163: (SCOUT, "VIP Perks Japan", ""), 164: (SCOUT, "DIVE JAPAN", "Clear Files"),
    165: (SCOUT, "SuperStar STARSHIP", "1"), 166: (SCOUT, "SuperStar STARSHIP", "2"),
    169: (FC, "DIVE 4", ""), 170: (FC, "DIVE 4", "DIVE JAPAN"),
    171: (SWIH, "Encore Blu-ray", "Blu-ray"), 172: (SWIH, "Encore Blu-ray", "Kit"), 173: (SWIH, "Encore Blu-ray", "Starship Square 特典"),
    174: (SWIH, "Encore Blu-ray", "Apple Music 特典"), 175: (SWIH, "Encore Blu-ray", "Ktown4U 特典"),
    181: (COLLAB, "公式ペンライト", "ver.2"),
    182: (SWIA, "Random Photocard Pack Korea", "1"), 183: (SWIA, "Random Photocard Pack Korea", "2"), 184: (SWIA, "Random Photocard Pack Korea", "3"),
    185: (SWIA, "Random Photocard Pack Korea", "4"), 186: (SWIA, "Random Photocard Pack Korea", "5"), 187: (SWIA, "Random Photocard Pack Korea", "6"),
    189: (SWIA, "Random Photocard Pack Japan", "1"), 190: (SWIA, "Random Photocard Pack Japan", "2"),
    191: (SWIA, "MD", "Chain Strap"), 192: (SWIA, "MD", "Smart Tok"), 193: (SWIA, "MD", "Ring"), 194: (SWIA, "MD", "Acrylic Stand"),
    195: (SWIA, "MD", "70K Benefit"), 196: (SWIA, "DIVE ZONE", "Day 1"), 197: (SWIA, "DIVE ZONE", "Day 2"), 198: (SWIA, "DIVE ZONE", "Day 3"),
    199: (SWIA, "SuperStar STARSHIP", "1"), 200: (SWIA, "SuperStar STARSHIP", "2"),
    203: (COLLAB, "SuperStar POP-UP", "Christmas"),
    206: (DII, "SuperStar STARSHIP", "1"), 207: (DII, "SuperStar STARSHIP", "2"), 208: (DII, "MD", "Photo Kit"),
}
DROP = set()  # 目で見て透かしがあった番号（bottom 確認のあとで書く）
if os.path.exists(SP + "na_leeseo_drop.json"):
    DROP = set(json.load(open(SP + "na_leeseo_drop.json")))


KEYS = [("yujin", "ユジン"), ("gaeul", "ガウル"), ("rei", "レイ"), ("wonyoung", "ウォニョン"), ("liz", "リズ")]


def nearest(bs, cx, cy, limit=160):
    b = min(bs, key=lambda b: abs((b[0] + b[2]) / 2 - cx) + abs((b[1] + b[3]) / 2 - cy))
    return b if abs((b[0] + b[2]) / 2 - cx) + abs((b[1] + b[3]) / 2 - cy) < limit else None


if __name__ == "__main__":
    miss = json.load(open(SP + "review/miss_na_leeseo.json", encoding="utf-8"))
    allrows = list(csv.DictReader(open(PROJ + "public/seed/cards.csv", encoding="utf-8")))
    have = set()
    for p in sorted(glob.glob(SP + "out/*.json")):
        if os.path.basename(p) in ("idalshiro_na_others.json",):
            continue
        for e in json.load(open(p, encoding="utf-8"))["images"]:
            have.add((e["collection"], tuple(e["members"]), e["source"], e["version"]))
    j = Job("idalshiro_na_others")
    for key, name in KEYS:
        im = grid.load(D + f"{key}_na.jpg")
        bs = grid.card_boxes(im, min_w=0.03, max_w=0.08)
        rows = [r for r in allrows if r["member"] == name]
        n = 0
        for idx, (csub, ssub, ver) in MAP.items():
            found = [r for r in rows if csub in r["collection"] and r["source"].startswith(ssub) and r["version"] == ver]
            if len(found) != 1:
                continue
            r = found[0]
            if (r["collection"], (name,), r["source"], r["version"]) in have or idx in DROP:
                continue
            x0, y0, x1, y1 = miss[idx][1]
            b = nearest(bs, (x0 + x1) / 2, (y0 + y1) / 2)
            if b is None:
                print("見つからない", name, idx); continue
            j.add(r["collection"], [name], r["source"], r["version"], im.crop(inset_frame(im, b)), CREDIT)
            n += 1
        print(name, n)
    j.save()
