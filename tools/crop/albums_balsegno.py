"""@balsegno の「IVE Liz Non Album / Merchandise」一覧（2026-04-19 版、HD 版 bit.ly/liz-template）

- 資料：pocamaster-images/_nonalbum/balsegno_liz/merch_1.jpg・merch_2.jpg（4000×7110）
- リズ 1 人分の表なので、種類（枠）は 6 人分作り、画像はリズの分だけ入れる（グッズ・特典はメンバー 1 人 1 種類）
- ユニットのカード（リズとだれか）は、相手を顔で決めることになるので入れない
- アプリにすでにある種類は入れない：
  IVE SCOUT の EMPATHY Soundwave ラキドロ（→ IVE EMPATHY「Soundwave ラキドロ 8.0 IVE SCOUT」）、
  愛知・横浜の会場特典（→ Be Alright「IVE SCOUT」）、DIVE ZONE Day 1（→「Day 1 IVE SCOUT ver.」）、
  SHOW WHAT I AM の京セラ 4/18・4/19（→ REVIVE+・LUCID DREAM「SWIA OSAKA exclusive」）、
  IVE SECRET Soundwave ラキドロ、4th ファンコンの REVIVE+ withmuu ラキドロ
"""
import grid
from build2 import *

D = ROOT + "_nonalbum/balsegno_liz/"
CREDIT = "@balsegno"
MEMBERS = ["ユジン", "ガウル", "レイ", "ウォニョン", "リズ", "イソ"]


def boxes(path, y_from):
    """カードの位置を上の段から、段の中は左から並べる"""
    im = grid.load(path)
    bs = sorted((b for b in grid.card_boxes(im, min_w=0.03, max_w=0.1) if b[1] > y_from), key=lambda b: (b[1] + b[3]) / 2)
    rows = []
    for b in bs:
        cy = (b[1] + b[3]) / 2
        if rows and abs(cy - rows[-1][0]) < 150:
            rows[-1][1].append(b)
        else:
            rows.append([cy, [b]])
    return im, [b for _, r in rows for b in sorted(r, key=lambda b: b[0])]


def outer(im, b):
    """白い縁のあるカード（ポラロイドなど）は、写真の部分しか見つからないので、薄い枠線まで広げる"""
    w, h = b[2] - b[0], b[3] - b[1]
    x0, y0, x1, y1 = int(b[0] - w * .2), int(b[1] - h * .15), int(b[2] + w * .2), int(b[3] + h * .4)
    a = np.asarray(im.crop((x0, y0, x1, y1))).astype(int)
    m = a.mean(axis=2) < 235
    # 下のラベルの文字を拾わないよう、写真の下の最初の空白の行で止める
    rows = m.any(axis=1)
    by = int(b[3] - y0)
    while by < len(rows) and rows[by]:
        by += 1
    # 上も同じ（上の段の線を拾わない）
    ty = int(b[1] - y0)
    while ty > 0 and rows[ty - 1]:
        ty -= 1
    m = m[ty:by]
    xs = np.nonzero(m.any(axis=0))[0]
    return (x0 + xs.min(), y0 + ty, x0 + xs.max(), y0 + by)


im1, b1 = boxes(D + "merch_1.jpg", 1100)
im2, b2 = boxes(D + "merch_2.jpg", 900)
assert len(b1) == 164 and len(b2) == 139, (len(b1), len(b2))

MAG = "2nd FANMEETING 'MAGAZINE IVE'"
SCOUT = "3rd FAN CONCERT 'IVE SCOUT'"
SWIA = "2nd WORLD TOUR 'SHOW WHAT I AM'"
FOURTH = "4th FAN CONCERT 'DIVE into IVE'"
DZ = "DIVE ZONE FC ブース特典"

# (コレクション, 入手元, バージョン, 表, 番号, 縁まで広げるか)
SETS = [
    *[(MAG, "Random Photocard Pack", str(i + 1), 1, 64 + i, False) for i in range(4)],
    (MAG, "MD", "Photo Kit", 1, 73, False),
    (MAG, "MD", "Polaroid", 1, 74, True),
    (MAG, "MD", "Photocard Holder", 1, 75, False),
    (MAG, "MD", "Acrylic Turning Stand", 1, 76, False),
    (MAG, "MD", "Cushion", 1, 77, False),
    (MAG, "Special Photocard", "Day 1", 1, 78, False),
    (MAG, "Special Photocard", "Day 2", 1, 79, False),
    *[(MAG, "SuperStar STARSHIP", str(i + 1), 1, 80 + i, False) for i in range(4)],

    (SCOUT, "Random Photocard Pack Japan", "1", 2, 15, False),
    (SCOUT, "Random Photocard Pack Japan", "2", 2, 16, False),
    (SCOUT, "MD", "Photo Kit", 2, 17, False),
    (SCOUT, "MD", "Acrylic Stand", 2, 18, False),
    (SCOUT, "MD", "Bandana", 2, 19, False),
    (SCOUT, "MD", "Whistle Necklace", 2, 20, False),
    (SCOUT, "MD", "Stainless Mug", 2, 21, False),
    (SCOUT, "MD", "Cereal Bowl + Spoon Set", 2, 22, False),
    (SCOUT, "DIVE JAPAN", "Clear Files", 2, 23, False),
    (SCOUT, "Lotte Cinema Live Viewing", "", 2, 24, False),
    (SCOUT, DZ, "Day 2", 2, 28, False),
    (SCOUT, "VIP Perks Japan", "", 2, 29, False),
    (SCOUT, "SuperStar STARSHIP", "1", 2, 34, False),
    (SCOUT, "SuperStar STARSHIP", "2", 2, 35, False),

    *[(SWIA, "Random Photocard Pack Korea", str(i + 1), 2, 82 + i, False) for i in range(6)],
    (SWIA, "Random Photocard Pack Japan", "1", 2, 89, False),
    (SWIA, "Random Photocard Pack Japan", "2", 2, 90, True),
    (SWIA, "MD", "Chain Strap", 2, 93, False),
    (SWIA, "MD", "Smart Tok", 2, 94, False),
    (SWIA, "MD", "Acrylic Stand", 2, 95, False),
    (SWIA, "MD", "Ring", 2, 96, False),
    (SWIA, "MD", "70K Benefit", 2, 97, False),
    (SWIA, DZ, "Day 1", 2, 98, False),
    (SWIA, DZ, "Day 2", 2, 99, False),
    (SWIA, DZ, "Day 3", 2, 100, False),
    (SWIA, "VIP Perks Japan", "", 2, 101, False),
    (SWIA, "SuperStar STARSHIP", "1", 2, 107, False),
    (SWIA, "SuperStar STARSHIP", "2", 2, 108, False),

    (FOURTH, "SuperStar STARSHIP", "1", 2, 134, False),
    (FOURTH, "SuperStar STARSHIP", "2", 2, 135, False),
]

if __name__ == "__main__":
    j = Job("balsegno_liz")
    for coll, src, ver, sheet, idx, wide in SETS:
        im, bs = (im1, b1) if sheet == 1 else (im2, b2)
        box = outer(im, bs[idx]) if wide else bs[idx]
        for m in MEMBERS:
            j.add(coll, [m], src, ver, im.crop(box) if m == "リズ" else None, CREDIT)
    j.save()
