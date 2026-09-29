"""@balsegno の「IVE Liz Non Album / Merchandise」一覧（2026-04-19 版、HD 版 bit.ly/liz-template）

- 資料：pocamaster-images/_nonalbum/balsegno_liz/merch_1.jpg・merch_2.jpg（4000×7110）
- リズ 1 人分の表なので、種類（枠）は 6 人分作り、画像はリズの分だけ入れる（グッズ・特典はメンバー 1 人 1 種類）
- ユニットのカード（リズとだれか）は、相手を顔で決めることになるので入れない
- Prom Queens DVD の Ktown4U 特典は、アプリの「特典（店舗不明）」と同じとみなした（ほかの種類が同じなので）
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

# 第 2 弾（2026-09-30）：アプリの画像（リズ）と写真で突き合わせ、見つからなかった種類。番号は上の段から数えた通し番号（表 1 は 900 から）
_, b1f = boxes(D + "merch_1.jpg", 900)
assert len(b1f) == 179, len(b1f)
COL = "Collab & Event｜コラボ・イベント"
MAGZ = "Magazine｜雑誌特典"
FC = "DIVE Official Fanclub｜ファンクラブ"
SWIH = "1st WORLD TOUR 'SHOW WHAT I HAVE'"
PROM = "1st FAN CONCERT 'The Prom Queens'"
PEPSI = "Pepsi × IVE 'BLUE & BLACK'"
PARK = "MINIVE POP-UP 'MINIVE PARK'"
SCHOOL = "MINIVE POP-UP 'MINIVE SCHOOL'"
BOOK = "1st PHOTOBOOK 'A Dreamy Day'"
DICON = "DICON 'I have a dream, I have a fantasy'"
ENC = "Encore（アンコール）"
ENCB = "Encore Blu-ray・Kit"
STAR = "SuperStar POP-UP 'STAR+ING: Christmas Bear'"
SETS2 = [
    # 表 1（通し番号）
    (COL, PARK, "Poca Binder", 3, 31, False), (COL, PARK, "Face Cushion", 3, 32, False), (COL, PARK, "Mega Cushion", 3, 33, False),
    (COL, PARK, "Pouch", 3, 34, False), (COL, PARK, "50K Benefit 1st week", 3, 35, False), (COL, PARK, "50K Benefit 2nd week", 3, 36, False),
    (COL, "SuperStar STARSHIP", "KCON LA", 3, 37, False), (COL, "SuperStar STARSHIP", "LONDON", 3, 38, False),
    (PROM, "DVD・Blu-ray・Kit", "DVD", 3, 54, False), (PROM, "DVD・Blu-ray・Kit", "Blu-ray", 3, 55, False),
    (PROM, "DVD・Blu-ray・Kit", "Kit", 3, 56, False), (PROM, "DVD・Blu-ray・Kit", "Kit POLA", 3, 57, True),
    (PROM, "DVD・Blu-ray・Kit", "Apple Music 特典", 3, 58, False), (PROM, "DVD・Blu-ray・Kit", "特典（店舗不明）", 3, 59, False),
    (COL, BOOK, "Pool Party ver.", 3, 64, False), (COL, BOOK, "Summer Beach Story ver.", 3, 65, False), (COL, BOOK, "Polaroid", 3, 66, True),
    (COL, BOOK, "Starship Square", 3, 67, False), (COL, BOOK, "withmuu", 3, 68, False),
    (COL, "MINIVE Christmas", "", 3, 69, False),
    (FC, "DIVE 3期 'IVE SCOUT'", "", 3, 75, False), (FC, "DIVE 3期 'IVE SCOUT'", "DIVE JAPAN", 3, 76, False),
    (FC, "DIVE JAPAN Phone Tab", "", 3, 77, False), (FC, "DIVE JAPAN Phone Tab", "FC 特典", 3, 78, False),
    (SWIH, "Thailand Random Photocard", "1", 3, 109, False), (SWIH, "Thailand Random Photocard", "2", 3, 110, False),
    (SWIH, "MD", "Trading Card Stand（東京ドーム）1", 3, 116, False), (SWIH, "MD", "Trading Card Stand（東京ドーム）2", 3, 117, False),
    (SWIH, "DIVE JAPAN", "Label Drink", 3, 118, False),
    ("IVE SWITCH", "LINE FRIENDS トレカ", "3", 3, 135, False), ("IVE SWITCH", "LINE FRIENDS トレカ", "4", 3, 137, False),
    ("IVE SWITCH", "LINE FRIENDS キーリング", "", 3, 138, False), ("IVE SWITCH", "LINE FRIENDS 特典", "3", 3, 141, False),
    (MAGZ, DICON, "Lucky Card Set 1", 3, 142, False), (MAGZ, DICON, "Lucky Card Set 2", 3, 143, False),
    (MAGZ, DICON, "Type A 1", 3, 144, False), (MAGZ, DICON, "Type A 2", 3, 145, False), (MAGZ, DICON, "Type A 3", 3, 146, False),
    (MAGZ, DICON, "Double Sided", 3, 148, False),
    (MAGZ, DICON, "Type B 1", 3, 149, False), (MAGZ, DICON, "Type B 2", 3, 150, False), (MAGZ, DICON, "Type B 3", 3, 151, False),
    (MAGZ, DICON, "Kakao 特典 1", 3, 153, False), (MAGZ, DICON, "Kakao 特典 2", 3, 154, False),
    (SWIH, ENC, "Random Photocard 1", 3, 155, False), (SWIH, ENC, "Random Photocard 2", 3, 156, False),
    (SWIH, ENC, "Wing Hair Pin Set", 3, 157, False), (SWIH, ENC, "Compact Mirror", 3, 158, False),
    (SWIH, ENC, "Photocard Holder Keyring", 3, 159, False), (SWIH, ENC, "DIVE ZONE Day 1", 3, 160, False),
    (SWIH, ENC, "DIVE ZONE Day 2", 3, 161, False), (SWIH, ENC, "SuperStar STARSHIP 1", 3, 162, False),
    (SWIH, ENC, "SuperStar STARSHIP 2", 3, 163, False),
    # 表 2
    (PEPSI, "IVE × PEPSI 2025", "1", 2, 4, False), (PEPSI, "IVE × PEPSI 2025", "2", 2, 5, False),
    (SWIH, ENCB, "Blu-ray", 2, 36, False), (SWIH, ENCB, "Kit", 2, 37, False), (SWIH, ENCB, "Apple Music 特典", 2, 38, True),
    (SWIH, ENCB, "Ktown4U 特典", 2, 39, False), (SWIH, ENCB, "Starship Square 特典", 2, 40, False),
    (FC, "DIVE 4期 'DIVE into IVE'", "", 2, 41, False), (FC, "DIVE 4期 'DIVE into IVE'", "DIVE JAPAN", 2, 42, False),
    (COL, "Papa John's", "7.0", 2, 45, False),
    (COL, SCHOOL, "Fluffy Plush", 2, 46, False), (COL, SCHOOL, "Hug Bag", 2, 47, False), (COL, SCHOOL, "70K Benefit", 2, 48, False),
    (COL, SCHOOL, "Shanghai MD 特典", 2, 49, False), (COL, SCHOOL, "Taipei & Kaohsiung MD 特典", 2, 50, False),
    (COL, "公式ペンライト", "ver.2", 2, 81, False),
    (COL, STAR, "Best", 2, 109, False), (COL, STAR, "Christmas", 2, 110, False), (COL, STAR, "Winter", 2, 111, False),
    (COL, STAR, "STAR+ING Tokyo", 2, 112, False),
]

# 第 3 弾（2026-09-30）：リズ 1 人の広告・特典（本人：実際にあるので、リズ個人のコレクションに入れる）。枠・画像ともリズだけ
LIZ = "Liz Solo｜リズ個人"
PC = "powercircles 'Colorful Summer'（2025.6）"
WV = "WAVES 漫潮 'Princess Thief'（2025.10）"
_dx = b2[56][0] - b2[53][0]
PC_C_POLA = (b2[56][0] + _dx, b2[56][1], b2[56][2] + _dx, b2[56][3])  # 見つからなかったポラロイド（set b のポラロイドから同じ間隔で右）
SETS3 = [
    (PC, "Set A 1", 51, False), (PC, "Set A 2", 52, False), (PC, "Set A POLA", 53, True),
    (PC, "Set B 1", 54, False), (PC, "Set B 2", 55, False), (PC, "Set B POLA", 56, True),
    (PC, "Set C 1", 57, False), (PC, "Set C 2", 58, False), (PC, "Set C POLA", PC_C_POLA, True),
    (PC, "Set D POLA 1", 59, True), (PC, "Set D POLA 2", 60, True), (PC, "Set D POLA 3", 61, True),
    (WV, "Set A 1", 62, False), (WV, "Set A 2", 63, False), (WV, "Set A POLA", 64, True),
    (WV, "Set B 1", 65, False), (WV, "Set B 2", 66, False), (WV, "Set B POLA", 67, True),
    (WV, "Set C 1", 68, False), (WV, "Set C 2", 69, False), (WV, "Set C POLA", 70, True),
    (WV, "Set D POLA 1", 71, True), (WV, "Set D POLA 2", 72, True), (WV, "Set D POLA 3", 73, True),
    ("8seconds", "1", 74, False), ("8seconds", "2", 75, False), ("8seconds", "3", 76, False),
    ("s.nature", "1", 77, False), ("s.nature", "2", 78, False), ("s.nature", "3", 79, False), ("s.nature", "4", 80, False),
    ("TONYMOLY", "1", 136, False), ("TONYMOLY", "2", 137, False), ("TONYMOLY", "3", 138, False),
]
# @an_chan_luv の SHOW WHAT I AM ソウル公演ランダムトレカの表にある全員のカード 4 枚（ID 入りの表なので枠だけ）
SWIA_IVE = [(SWIA, "Random Photocard Pack Korea", f"IVE {i}") for i in range(1, 5)]

LIZ_ONLY = {(MAG, "MD", "Cushion"), (SCOUT, "MD", "Cereal Bowl + Spoon Set")}

if __name__ == "__main__":
    j = Job("balsegno_liz")
    for coll, src, ver, sheet, idx, wide in SETS:
        im, bs = (im1, b1) if sheet == 1 else (im2, b2)
        box = outer(im, bs[idx]) if wide else bs[idx]
        # メンバーごとに品物が違うグッズは、リズの分だけ（ほかのメンバーは albums_idalshiro.py）
        for m in (["リズ"] if (coll, src, ver) in LIZ_ONLY else MEMBERS):
            j.add(coll, [m], src, ver, im.crop(box) if m == "リズ" else None, CREDIT)
    for coll, src, ver, sheet, idx, wide in SETS2:
        im, bs = (im1, b1f) if sheet == 3 else (im2, b2)
        box = outer(im, bs[idx]) if wide else bs[idx]
        for m in MEMBERS:
            j.add(coll, [m], src, ver, im.crop(box) if m == "リズ" else None, CREDIT)
    for src, ver, idx, wide in SETS3:
        b = idx if isinstance(idx, tuple) else b2[idx]
        j.add(LIZ, ["リズ"], src, ver, im2.crop(outer(im2, b) if wide else b), CREDIT)
    for coll, src, ver in SWIA_IVE:
        j.add(coll, ["全員"], src, ver)
    j.save()
