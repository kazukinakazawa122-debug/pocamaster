"""@idalshiro の「IVE photocard template — all IVE photocards & pobs」メンバー別（2026-08-31 版、HD 版 tinyurl.com/idalshiro）

- 資料：pocamaster-images/_nonalbum/idalshiro/<メンバー>_1〜3.jpg（アルバム）・<メンバー>_na.jpg（ノンアルバム）。4500×8000
- 表の下に作者名（idalshiro）があるだけで、カードに ID はない。出典に @idalshiro を記録する（作者の希望：名前を消さない）
- 6 人とも同じ並びなので、同じ位置のカードは同じ種類。ラベルは目で読んだ（2026-09-30）
- ここで入れるもの：
  - メンバーごとに品物が違うグッズ（@balsegno の表はリズだけなので、6 人同じだとまちがえていた）
    MAGAZINE IVE：Tumbler・Scarf・Fur Pouch・Slippers・Cushion・Blanket
    IVE SCOUT：Rug・String Pouch・Backpack・Neck Pillow・Cereal Bowl + Spoon Set・Hoodie
  - SHOW WHAT I AM：VIP Perks USA、SWIA TAIPEI の特典 4 種、SuperStar STARSHIP の PARIS・LA・MEXICO
"""
import grid
from build2 import *

D = ROOT + "_nonalbum/idalshiro/"
CREDIT = "@idalshiro"
KEYS = [("yujin", "ユジン"), ("gaeul", "ガウル"), ("rei", "レイ"), ("wonyoung", "ウォニョン"), ("liz", "リズ"), ("leeseo", "イソ")]

MAG = "2nd FANMEETING 'MAGAZINE IVE'"
SCOUT = "3rd FAN CONCERT 'IVE SCOUT'"
SWIA = "2nd WORLD TOUR 'SHOW WHAT I AM'"
MAG_ITEM = {"ユジン": "Tumbler", "ガウル": "Scarf", "レイ": "Fur Pouch", "ウォニョン": "Slippers", "リズ": "Cushion", "イソ": "Blanket"}
SCOUT_ITEM = {"ユジン": "Rug", "ガウル": "String Pouch", "レイ": "Backpack", "ウォニョン": "Neck Pillow", "リズ": "Cereal Bowl + Spoon Set", "イソ": "Hoodie"}
# @balsegno（リズだけの表）から 6 人分作ってしまった枠。リズ以外は消す（merge.py の DROP）
WRONG = [(MAG, "MD", "Cushion"), (SCOUT, "MD", "Cereal Bowl + Spoon Set")]

# ノンアルバムの表（_na.jpg）の中のカードのおおよその中心 (x, y)
SETS = [
    (MAG, "MD", MAG_ITEM, (1306, 2783)),
    (SCOUT, "MD", SCOUT_ITEM, (1935, 4465)),
    (SWIA, "VIP Perks USA", "", (2991, 5305)),
    (SWIA, "SWIA TAIPEI 特典", "Waffer", (240, 6550)),
    (SWIA, "SWIA TAIPEI 特典", "Holder", (441, 6550)),
    (SWIA, "SWIA TAIPEI 特典", "Early Bird", (654, 6550)),
    (SWIA, "SWIA TAIPEI 特典", "Mnet+", (870, 6550)),
    (SWIA, "SuperStar STARSHIP", "PARIS", (216, 6136)),
    (SWIA, "SuperStar STARSHIP", "LA", (4260, 5734)),
    (SWIA, "SuperStar STARSHIP", "MEXICO", (1086, 6550)),
]


def nearest(bs, pt, limit=150):
    b = min(bs, key=lambda b: abs((b[0] + b[2]) / 2 - pt[0]) + abs((b[1] + b[3]) / 2 - pt[1]))
    d = abs((b[0] + b[2]) / 2 - pt[0]) + abs((b[1] + b[3]) / 2 - pt[1])
    return b if d < limit else None


if __name__ == "__main__":
    j = Job("idalshiro")
    for key, name in KEYS:
        im = grid.load(D + f"{key}_na.jpg")
        bs = grid.card_boxes(im, min_w=0.03, max_w=0.08)
        for coll, src, ver, pt in SETS:
            v = ver[name] if isinstance(ver, dict) else ver
            b = nearest(bs, pt)
            if b is None:
                print("見つからない", name, src, v)
            j.add(coll, [name], src, v, im.crop(b) if b else None, CREDIT)
    j.save()
