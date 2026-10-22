"""2026-10-22：X で探した資料で、画像なしの枠を埋める（本人「Claude in Chrome で新しい画像を探して」。保存は本人の了承ずみ）
資料は pocamaster-images/新しい資料 2026-10-22/（X の元の大きさ）

- pepsi2025_2_yangdo0x.jpg（@yangdo0x の実物の写真 2048×2048）：Pepsi 2025「2」（2025-07-30〜 ペプシ ゼロ ライムの特典）6 人。
  カードに名前が印刷されている。リズの「2」も @balsegno の 205px から差し替え
- pepsi2025_1_originalwy.jpg（ペプシの告知画像 738×608、@originalwy の投稿）：Pepsi 2025「1」（2025-03 の A・B セット）。
  名前がないので本人が決めた（2026-10-22）。リズは @balsegno の画像の方が大きいので入れない
- papajohns7_ANNYEONZ_.jpg（@ANNYEONZ_ の実物の写真 1536×2048）：Papa John's 7.0（プリズム フォトカード）。
  名前がないので本人が決めた（2026-10-22）。リズ（三つ編み）は @balsegno の 7.0 と同じ写真 → 206px から差し替え
- staring_tokyo_takasi_0818.jpg（@takasi_0818 の投稿 498×508）：STAR+ING Tokyo。カードに名前が印刷されている。
  SuperStar STORE の斜めの文字は使ってよい（本人、2026-10-22）。リズは @balsegno の画像の方が大きいので入れない
- 使わなかったもの：1st PHOTOBOOK の withmuu・Starship Square の告知（ぼかし入りで、カードが重なっている）
- 実物の写真は 4 つの角を拡大した方眼で読み、55:85 にゆがみを直した（四辺から 1% 内側）
"""
import numpy as np
from PIL import Image
from build2 import *

D = ROOT + "新しい資料 2026-10-22/"
PEPSI = "Pepsi × IVE 'BLUE & BLACK'"
COLLAB = "Collab & Event｜コラボ・イベント"


def coeffs(src, dst):
    A, B = [], []
    for (x, y), (X, Y) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -X * x, -X * y]); B.append(X)
        A.append([0, 0, 0, x, y, 1, -Y * x, -Y * y]); B.append(Y)
    return np.linalg.solve(np.array(A, float), np.array(B, float))


def warp(im, quad, H=1100, inset=0.01):
    """quad：左上・右上・右下・左下"""
    W = round(H * 55 / 85)
    q = np.array(quad, float); c = q.mean(0); q = c + (q - c) * (1 - inset)
    return im.transform((W, H), Image.PERSPECTIVE, coeffs(q, [(0, 0), (W, 0), (W, H), (0, H)]), Image.BICUBIC)


PEPSI2 = {"ウォニョン": [(240, 215), (733, 213), (742, 932), (205, 935)], "イソ": [(745, 212), (1213, 212), (1250, 925), (748, 928)],
          "リズ": [(1222, 225), (1675, 230), (1700, 925), (1262, 930)], "ガウル": [(196, 960), (740, 955), (744, 1838), (160, 1862)],
          "ユジン": [(745, 938), (1258, 935), (1322, 1792), (758, 1822)], "レイ": [(1270, 956), (1756, 940), (1870, 1770), (1324, 1810)]}
PAPA7 = {"ガウル": [(185, 371), (573, 389), (563, 973), (165, 968)], "ユジン": [(592, 384), (957, 384), (947, 968), (579, 963)],
         "ウォニョン": [(978, 399), (1362, 399), (1370, 993), (978, 988)], "リズ": [(182, 1014), (566, 1019), (566, 1646), (169, 1649)],
         "レイ": [(596, 1014), (963, 1014), (968, 1628), (599, 1631)], "イソ": [(985, 1022), (1357, 1024), (1370, 1649), (985, 1651)]}
PEPSI1 = {"ウォニョン": (110, 115, 221, 298), "レイ": (230, 115, 344, 298), "ガウル": (352, 115, 467, 298),
          "ユジン": (110, 335, 221, 519), "イソ": (352, 335, 467, 519)}
STARING = {"ユジン": (0, 3, 148, 248), "ガウル": (169, 3, 320, 248), "レイ": (341, 3, 493, 248),
           "ウォニョン": (0, 267, 148, 508), "イソ": (341, 267, 493, 508)}

if __name__ == "__main__":
    j = Job("zzzzzzzzzzzzzzzzzzzzz_x_1022")
    im = Image.open(D + "pepsi2025_2_yangdo0x.jpg").convert("RGB")
    for m, q in PEPSI2.items():
        j.add(PEPSI, [m], "IVE × PEPSI 2025", "2", warp(im, q), "@yangdo0x")
    im = Image.open(D + "papajohns7_ANNYEONZ_.jpg").convert("RGB")
    for m, q in PAPA7.items():
        j.add(COLLAB, [m], "Papa John's", "7.0", warp(im, q), "@ANNYEONZ_")
    im = Image.open(D + "pepsi2025_1_originalwy.jpg").convert("RGB")
    for m, b in PEPSI1.items():
        j.add(PEPSI, [m], "IVE × PEPSI 2025", "1", im.crop(b), "Pepsi（@originalwy の投稿）")
    im = Image.open(D + "staring_tokyo_takasi_0818.jpg").convert("RGB")
    for m, b in STARING.items():
        j.add(COLLAB, [m], "SuperStar POP-UP 'STAR+ING: Christmas Bear'", "STAR+ING Tokyo", im.crop(b), "@takasi_0818")
    j.save()
