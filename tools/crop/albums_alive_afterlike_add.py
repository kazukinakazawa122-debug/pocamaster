"""ALIVE の会場限定盤と After LIKE の Music Korea ファンサイン当選特典（本人が 2026-10-01 に入れた。pocamaster-images/新しい資料 2026-10-01/ALIVE・After LIKE 追加分/）

- ALIVE_会場限定盤.png（実物の写真の画面写真。2 段×3 列）：並びは ユジン・ガウル・レイ／ウォニョン・リズ・イソ
  （アプリの既存の 4 枚と同じ写真で確認：ユジン 0.71・ガウル 0.67・レイ 0.90・リズ 0.59）。画像のなかったウォニョン・イソだけ入れる
- AfterLIKE_musickorea_fansign_pvc_reina831wy.jpg：@reina831wy の「music korea fansign event winner benefit pvc photocard set」
  （メンバー 6 枚＋全員のカード 3 枚）。アプリの After LIKE「MusicArt」は名前がちがい、これが正しい（本人。Tower Records に似ているが別のもの）
  → 枠を「Music Korea ファンサイン当選特典｜PVC フォトカードセット」にして 6 人とも画像あり。全員のカード 3 枚（GROUP 1〜3）の枠も足す
"""
from PIL import Image
import grid
from build2 import *

D = ROOT + "新しい資料 2026-10-01/ALIVE・After LIKE 追加分/"
M = ["ユジン", "ガウル", "レイ", "ウォニョン", "リズ", "イソ"]
SRC = "Music Korea ファンサイン当選特典"
if __name__ == "__main__":
    j = Job("zzzzzzzzzz_alive_afterlike")
    k = 1284 / 693
    im = Image.open(D + "ALIVE_会場限定盤.png").convert("RGB")
    cs = [(82, 262), (266, 447), (452, 636)]; rs = [(463, 737), (747, 1033)]
    for i, m in enumerate(M):
        if m in ("ウォニョン", "イソ"):
            (x0, x1), (y0, y1) = cs[i % 3], rs[i // 3]
            j.add("ALIVE", [m], "本体封入", "会場限定盤", im.crop((int(x0 * k) + 3, int(y0 * k) + 3, int(x1 * k) - 3, int(y1 * k) - 3)), "本人の写真")
    s = grid.load(D + "AfterLIKE_musickorea_fansign_pvc_reina831wy.jpg")
    bs = sorted((b for b in grid.card_boxes(s, min_w=0.1, max_w=0.3, ratio=(1.3, 1.7)) if b[1] > 350), key=lambda b: (round((b[1] + b[3]) / 2 / 400), b[0]))
    order = ["ガウル", "ユジン", "レイ", "ウォニョン", "リズ", "イソ"]
    assert len(bs) == 6
    for m, b in zip(order, bs):
        j.add("After LIKE", [m], SRC, "PVC フォトカードセット", s.crop(tuple(int(v) for v in b)), "@reina831wy")
    for n, (x0, y0, x1, y1) in enumerate([(412, 1430, 743, 1644), (779, 1430, 1111, 1644), (1144, 1430, 1477, 1644)], start=1):
        j.add("After LIKE", ["全員"], SRC, f"PVC GROUP {n}", s.crop((x0, y0, x1, y1)), "@reina831wy")
    # LOVE DIVE の Jewel ver. 9set POB の Group Photocard 1・2（表の左＝1、右＝2。本人が 2026-10-01 に入れた）
    ld = Image.open(ROOT + "新しい資料 2026-10-01/LOVE DIVE 追加分/LOVEDIVE_Jewel_9set_POB_group_reina831wy.jpg").convert("RGB")
    k2 = 1996 / 1500
    for n, (x0, y0, x1, y1) in enumerate([(224, 922, 472, 1306), (522, 922, 770, 1306)], start=1):
        j.add("LOVE DIVE", ["全員"], "Jewel ver. 9set POB", f"Group Photocard {n}", ld.crop((int(x0 * k2) + 2, int(y0 * k2) + 2, int(x1 * k2) - 2, int(y1 * k2) - 2)), "@reina831wy")
    j.save()
