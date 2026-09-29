"""2026-09-29 に本人が追加した資料（pocamaster-images/新しい資料 2026-09-29/）から枠と画像を作る

資料の番号は、ファイル名の順（0〜28）。カードの番号は、card_boxes で見つけた箱を読む順に並べたもの
（確認用の画像で 1 つずつ見て決めた）。メンバーの並びは表に印刷された名前（YUJIN GAEUL REI WONYOUNG LIZ LEESEO）。
"""
import os
import numpy as np
from PIL import Image
from build2 import *

D = ROOT + "新しい資料 2026-09-29/"
FILES = sorted(os.listdir(D))
M = ["ユジン", "ガウル", "レイ", "ウォニョン", "リズ", "イソ"]  # 表の列の順
ALL = ["全員"]
LILY = "@LILY_221019"
G = "グッズ｜"


def seq(i):
    im = grid.load(D + FILES[i])
    bs = grid.card_boxes(im, ratio=(0.55, 1.9), min_w=0.035, max_w=0.4)
    bs.sort(key=lambda b: (b[1] + b[3]) / 2)
    rows = []
    for b in bs:
        cy, h = (b[1] + b[3]) / 2, b[3] - b[1]
        if rows and abs(cy - rows[-1][0]) < h * 0.35:
            rows[-1][1].append(b)
        else:
            rows.append([cy, [b]])
    return im, [b for _, r in rows for b in sorted(r, key=lambda b: b[0])]


_cache = {}


def sheet(i):
    if i not in _cache:
        _cache[i] = seq(i)
    return _cache[i]


def crop(i, k):
    im, s = sheet(i)
    return im.crop(tuple(int(v) for v in s[k]))


def row(j, i, ks, coll, src, ver, credit=LILY, members=None):
    """ks：6 人分のカードの番号（表の列の順）"""
    for k, m in zip(ks, members or [[x] for x in M]):
        j.add(coll, m, src, ver, None if k is None else crop(i, k), credit)


def r6(a):
    return list(range(a, a + 6))


# ---------- コラボ・イベント ----------
C = "Collab & Event｜コラボ・イベント"
j = Job("new_collab")
E = "ForEVER IVE（エバーランド）"
row(j, 0, r6(9), C, E, "MD MINIVE HUG BAG")
row(j, 0, r6(15), C, E, "Special Gift 70K")
row(j, 0, r6(22), C, E, "PASS")
row(j, 0, r6(29), C, E, "Special Reward")
row(j, 15, r6(16), C, E, "Special Gift 70K 2.0（8.21〜）")
row(j, 15, r6(23), C, E, "PASS 2.0")
row(j, 15, r6(30), C, E, "Special Reward 2.0")
row(j, 14, r6(1), C, "Dive into MINIVE", "MD MINIVE MINI HANDY FAN")
row(j, 14, r6(8), C, "Dive into MINIVE", "Special Gift 70K")
P = "PUMA"
row(j, 3, r6(1), C, P, "1.0 TEVERIS NITRO")
row(j, 3, r6(7), C, P, "2.0 PALERMO（China）")
row(j, 3, r6(20), C, P, "3.0 PALERMO")
row(j, 3, r6(27), C, P, "4.0 WAVEMULE")
K = "光東 とうもろこしのひげ茶"
row(j, 5, r6(0), C, K, "1.0")
row(j, 5, r6(12), C, K, "2.0")
row(j, 5, r6(24), C, K, "3.0")
j.add(C, ALL, K, "3.0 ALL", crop(5, 36), LILY)
PJ = "Papa John's"
for a, v in [(0, "1.0"), (7, "2.0"), (13, "3.0"), (20, "4.0 クリア"), (27, "5.0"), (34, "6.0 レンチキュラー")]:
    row(j, 13, r6(a), C, PJ, v)
W1 = "AMUSE スティックウエハース"
for a, v in [(0, "Normal A"), (6, "Normal B"), (12, "Normal C"), (18, "Rare solo")]:
    row(j, 6, r6(a), C, W1, v)
for k, v in zip([25, 26, 27, 28], "ABCD"):
    j.add(C, ALL, W1, f"Rare all {v}", crop(6, k), LILY)
for k, mem in [(29, ["ガウル", "ユジン"]), (30, ["レイ", "リズ"]), (31, ["ウォニョン", "イソ"])]:
    j.add(C, mem, W1, "Rare unit", crop(6, k), LILY)
j.add(C, ALL, W1, "Secret", crop(6, 32), LILY)
W2 = "AMUSE ウエハース2"
for a, n in [(1, 1), (7, 7), (13, 13)]:
    for d in range(6):
        j.add(C, [M[d]], W2, f"N-{n + d:02d}", crop(2, a + d), LILY)
for d in range(6):
    j.add(C, [M[d]], W2, f"R-{19 + d:02d}", crop(2, 19 + d), LILY)
for k, v in [(25, "R-25 縦"), (27, "R-26 横（白）"), (28, "R-27 横（赤）")]:
    j.add(C, ALL, W2, v, crop(2, k), LILY)
j.save()

# ---------- ペプシ ----------
C = "Pepsi × IVE 'BLUE & BLACK'"
j = Job("new_pepsi")
for a, s, v in [(0, "2023", "1.0 A"), (13, "2023", "1.0 B"), (25, "2023", "2.0 クリア"), (37, "2023", "3.0"), (49, "2023", "4.0"),
                (7, "2024", "5.0 A"), (19, "2024", "5.0 B"), (31, "2024", "6.0 A"), (43, "2024", "6.0 B"), (55, "2024", "6.0 C"),
                (62, "2024", "7.0 A"), (69, "2024", "7.0 B")]:
    row(j, 12, r6(a), C, f"IVE × PEPSI {s}", v)
j.save()

# ---------- 音楽番組 ----------
j = Job("new_broadcast")
row(j, 17, r6(0), "Music Show & Broadcast｜音楽番組・公開放送", "2024 KBS 歌謡大祝祭", "")
j.save()

# ---------- シーグリ ----------
j = Job("new_ssgt")
C = "2025 SEASON'S GREETINGS [Colorful Days with IVE]"
row(j, 25, r6(0), C, "本体封入", "フォトカードセット")
row(j, 25, r6(7), C, "Starship Square", "")
row(j, 25, r6(14), C, "Soundwave", "")
row(j, 25, r6(21), C, "Ktown4U", "")
C = "2026 SEASON'S GREETINGS [ATELIER IVE]"
row(j, 28, r6(4), C, "本体封入", "フォトカードセット")
row(j, 28, r6(11), C, "Starship Square", "")
row(j, 28, r6(18), C, "withmuu", "")
row(j, 28, r6(25), C, "MINIVE シーグリ Starship Square", "")
j.save()

# ---------- IVE SCOUT ----------
j = Job("new_scout")
C = "3rd FAN CONCERT 'IVE SCOUT'"
im, s = sheet(26)
solo = {"ユジン": [0, 1, 2, 3], "ガウル": [4, 5, 6, 7], "レイ": [8, 9, 10, 11], "ウォニョン": [12, 13, 14, 15],
        "リズ": [16, "17L", "17R", 18], "イソ": [19, 20, 21, 22]}
for m, ks in solo.items():
    for n, k in enumerate(ks, 1):
        if isinstance(k, str):  # 2 枚が 1 つにつながって見つかったので、左右に分ける
            b = s[17]
            mid = (b[0] + b[2]) / 2
            box = (b[0], b[1], mid - 6, b[3]) if k.endswith("L") else (mid + 6, b[1], b[2], b[3])
            img = im.crop(tuple(int(v) for v in box))
        else:
            img = crop(26, k)
        j.add(C, [m], "Random Photocard Pack", str(n), img, LILY)
row(j, 24, r6(0), C, "DIVE ZONE FC ブース特典", "Day 1 IVE SCOUT ver.")
j.save()

# ---------- ツアー ----------
j = Job("new_tour")
C = "2nd WORLD TOUR 'SHOW WHAT I AM'"
S = "DIVE JAPAN オンラインくじ C賞（京セラドーム）"
row(j, 1, r6(2), C, S, "①")
row(j, 1, r6(8), C, S, "②")
row(j, 1, r6(14), C, S, "③")
for n, k in enumerate([21, 22, 23], 1):
    j.add(C, ["ユジン", "リズ", "イソ"], S, f"UNIT {'①②③'[n - 1]}", crop(1, k), LILY)
for n, k in enumerate([24, 25, 26], 1):
    j.add(C, ["ガウル", "レイ", "ウォニョン"], S, f"UNIT {'①②③'[n - 1]}", crop(1, k), LILY)
for n, k in enumerate([28, 29, 30], 1):
    j.add(C, ALL, S, f"IVE {'①②③'[n - 1]}", crop(1, k), LILY)
C = "1st WORLD TOUR 'SHOW WHAT I HAVE'"
S = "DVD・Blu-ray・Kit"
for a, v in [(1, "DVD"), (8, "Blu-ray"), (14, "Kit"), (20, "Starship Square 特典"), (26, "Apple Music 特典"), (32, "Ktown4U 特典")]:
    row(j, 22, r6(a), C, S, v)
# in CINEMA：背景が黒く自動で見つからないので、位置を測って切り出す
im = grid.load(D + FILES[4])
xs = [199, 280, 360, 440, 516, 594]
ys = [310, 430, 548, 667, 786, 906, 1024, 1143, 1263]
f = im.width / 700
cw, ch = 67, 101
for y, v in zip(ys, ["Acryl Photocard Stand", "Photocard Pouch", "Photo Set", "Quick Snap", "Tumbler", "Light Stick Bag",
                     "70K Benefit（self photocard）", "70K Benefit（NFT photocard）", "2nd Week 入場特典"]):
    for x, m in zip(xs, M):
        box = ((x - cw / 2) * f, (y - ch / 2) * f, (x + cw / 2) * f, (y + ch / 2) * f)
        j.add(C, [m], "in CINEMA", v, im.crop(tuple(int(t) for t in box)), LILY)
j.save()

# ---------- 4th ファンコン ----------
j = Job("new_fancon4")
C = "4th FAN CONCERT 'DIVE into IVE'"
for m, a in zip(M, [0, 12, 24, 36, 48, 61]):
    for n in range(6):
        j.add(C, [m], "Random Photocard Pack", str(n + 1), crop(19, a + n), LILY)
j.add(C, ["ユジン", "ガウル", "リズ"], "Random Photocard Pack", "UNIT", crop(19, 79), LILY)
j.add(C, ["レイ", "ウォニョン", "イソ"], "Random Photocard Pack", "UNIT", crop(19, 80), LILY)
j.add(C, ALL, "Random Photocard Pack", "IVE 1", crop(19, 81), LILY)
j.add(C, ALL, "Random Photocard Pack", "IVE 2", crop(19, 82), LILY)
row(j, 19, [6, 7, 8, 9, 10, None], C, "MD", "Photo Kit")  # イソの枠は資料が空欄
row(j, 19, r6(18), C, "MD", "Acrylic Stand Set")
row(j, 19, r6(30), C, "MD", "Collect Book")
row(j, 19, r6(42), C, "MD", "Locket Pendant Necklace")
im, s = sheet(19)
for d, k in enumerate([54, 55, 56, 57, None, 59]):
    if k is None:  # リズの T シャツのカードは上下 2 つに分かれて見つかったので、合わせる
        a, b = s[58], s[59]
        img = im.crop((int(a[0]), int(a[1]), int(a[2]), int(b[3])))
    else:
        img = crop(19, k)
    j.add(C, [M[d]], "MD", "T-shirt", img, LILY)
row(j, 19, r6(67), C, "MD", "Designed by the members")
row(j, 19, r6(73), C, "MD", "70K Benefit")
j.save()

# ---------- ALIVE（@ri__chan94。列の並びは他の表と同じ YUJIN〜LEESEO とみなす）----------
j = Job("new_alive")
C = "ALIVE"
RC = "@ri__chan94"
for a, s_, v in [(0, "本体封入", "Album A（I ver.）"), (12, "本体封入", "Album B（II ver.）"), (24, "本体封入", "Normal ED（III ver.）"),
                 (36, "本体封入", "Solo（IV ver.）"), (49, "本体封入", "Limited ED（V ver.）"), (73, "本体封入", "Clear Photocard"),
                 (61, "Sony Music Shop", "オンライン ラキドロ"), (97, "Tower Records", "Selca Photocard #B"),
                 (6, "HMV・LAWSON", "Selca Photocard #C"), (18, "オフラインイベント", "8/16 OSAKA"), (30, "オフラインイベント", "8/19 TOKYO"),
                 (42, "Japan CD Shop ラキドロ", ""), (55, "Tower Records Shibuya", "限定抽選 A賞"), (91, "Sony Music Shop", "期間限定特典")]:
    ks = r6(a)
    if a == 42:
        ks = [42, 43, 44, "45+48", 46, 47]  # 4 枚目は上下 2 つに分かれて見つかったので、合わせる
    for k, m in zip(ks, M):
        if isinstance(k, str):
            im, s = sheet(10)
            b1, b2 = s[45], s[48]
            img = im.crop((int(min(b1[0], b2[0])), int(min(b1[1], b2[1])), int(max(b1[2], b2[2])), int(max(b1[3], b2[3]))))
        else:
            img = crop(10, k)
        j.add(C, [m], s_, v, img, RC)
# 10/13 東京・10/14 大阪 オフラインイベントのユニットカード（@ri__chan94 の X の投稿で確認。枠だけ、2026-09-29）
for day in ["10/13 TOKYO ユニット", "10/14 OSAKA ユニット"]:
    for pair in [["ウォニョン", "ユジン"], ["ユジン", "イソ"], ["ガウル", "イソ"], ["ガウル", "リズ"], ["レイ", "リズ"], ["レイ", "ウォニョン"]]:
        j.add(C, pair, "オフラインイベント", day)
j.save()

# ---------- Be Alright：全員の表（20）から切り、メンバー別の表（大きい）に同じ写真があれば差し替える ----------
PER = {8: "リズ", 11: "レイ", 16: "ユジン", 18: "イソ", 23: "ウォニョン", 27: "ガウル"}


def feat(img):
    w, h = img.size
    a = np.asarray(img.crop((w * .1, h * .1, w * .9, h * .9)).convert("RGB").resize((24, 36), Image.BILINEAR)).astype(float)
    a = a - a.mean(axis=(0, 1))
    a = a / (a.std() + 1e-6)
    return a.flatten() / np.sqrt(a.size)


cands = []
for i, mem in PER.items():
    im, s = sheet(i)
    for b in s:
        c = im.crop(tuple(int(v) for v in b))
        cands.append((mem, c, feat(c)))

j = Job("new_bealright")
C = "Be Alright"
BA = [(0, "本体封入", "初回生産限定盤 I"), (12, "本体封入", "初回生産限定盤 V"), (24, "本体封入", "初回生産限定盤 E"),
      (48, "本体封入", "ソロジャケット盤"), (60, "IVE SCOUT", "愛知・福岡 1日目"), (72, "IVE SCOUT", "愛知・福岡 2日目"),
      (84, "IVE SCOUT", "神戸・横浜 1日目"), (91, "IVE SCOUT", "神戸・横浜 2日目"),
      (6, "A!SMART", "A"), (18, "Tower Records", "B"), (30, "HMV", "C"), (42, "Sony Music", "クリアフォトカード"),
      (54, "Sony Music ラキドロ", ""), (66, "Tower Records Shibuya", "限定フォトカード（抽選）"), (78, "全店ラキドロ", "")]
log = []
seen = {}
for a, s_, v0 in BA + [(36, "本体封入", "通常盤 ユニット")]:
    for d in range(6):
        v = v0
        small = crop(20, a + d)
        fs = feat(small)
        sc = [(float(fs @ f_), mem, c) for mem, c, f_ in cands]
        hit = [x for x in sc if x[0] > 0.85]
        if a == 36:  # ユニット：同じ写真が入っているメンバー別の表のメンバー
            mem = sorted({x[1] for x in hit}, key=M.index)
        else:
            mem = [M[d]]
            if hit and {x[1] for x in hit} != {M[d]}:
                log.append(("メンバーが合わない", s_, v, M[d], sorted({x[1] for x in hit})))
        if a == 36:
            seen[tuple(mem)] = seen.get(tuple(mem), 0) + 1
            v = f"通常盤 ユニット {seen[tuple(mem)]}"
        best = max(sc)
        img = best[2] if best[0] > 0.85 and min(best[2].size) > min(small.size) else small
        log.append((s_, v, "/".join(mem), round(best[0], 3), img.size))
        j.add(C, mem, s_, v, img, LILY)
# 日本のオフラインイベント（@LILY_221019 の一覧 ver.5、2025-10 で追加された分。IVE SECRET の同じ日付のカードとは別の写真）。枠だけ（2026-09-29）
for v in ["9.23 TOKYO", "9.24 OSAKA", "10.12 TOKYO", "10.13 OSAKA"]:
    for m in M:
        j.add(C, [m], "オフラインイベント", v)
j.save()
for l in log:
    print(*l)
