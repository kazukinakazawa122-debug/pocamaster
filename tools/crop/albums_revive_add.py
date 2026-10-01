"""REVIVE+ の足りない画像（本人が 2026-10-01 にフォルダへ入れた資料。pocamaster-images/新しい資料 2026-10-01/REVIVE+ 追加分/）

- HIT_MAGAZINE_POB_nishitemplates.jpg：「IVE x HIT MAGAZINE POB」6 人（上段ユジン・ガウル・レイ、下段ウォニョン・リズ・イソ）→ HIT! MAGAZINE。
  作者 @nishitemplates の名前は表の上の画像の隅にあるだけ（カードには写っていない）
- wishlist_Gaeul_idalshiro.jpg：@idalshiro のガウルの REVIVE+ wishlist（11 列 × 9 段。列 x=56+405c・段 y=1338+702r・カード 326×506）
  - 7 段目の 1 枚目「KMONSTAR」→ ガウルの KMONSTAR 2.0（本人：ガウルの全種類の KMONSTAR と書いてある所）
- wishlist_Yujin_idalshiro.jpg：ユジンの同じ表。4 段目の 2 枚目「QQ MUSIC member set」→ ユジンの QQ Music Membership（＝Member set。本人、2026-10-01）
- QQ_random5_6cards.jpg：QQ Music 2.0 ランダム 5 の 6 人分（ガウル・ユジン・レイ・ウォニョン・リズ・イソの順。ユジンの表の「tjxxx」の ID 入りと同じ写真で確かめた）→ ユジンの ランダム 5（ID のないきれいな画像）
- QQ Music の「Membership」と「Member set 2」は同じカード（本人）：Membership に一本化し、Member set 2 の枠は消す。
  画像のなかったイソ・ウォニョンの Membership には、Member set 2 の画像を入れる
- 「本体封入 Vinyl」はまだ発表されていないので枠を消す（本人）
"""
import csv, glob, json, os
from PIL import Image
import grid
from build2 import *

D = ROOT + "新しい資料 2026-10-01/REVIVE+ 追加分/"
C = "REVIVE+"
box = lambda r, c: (56 + 405 * c, 1338 + 702 * r, 56 + 405 * c + 326, 1338 + 702 * r + 506)
ORDER = ["ユジン", "ガウル", "レイ", "ウォニョン", "リズ", "イソ"]
if __name__ == "__main__":
    j = Job("revive_add")
    hm = grid.load(D + "HIT_MAGAZINE_POB_nishitemplates.jpg")
    bs = sorted(grid.card_boxes(hm, min_w=0.1, max_w=0.3, ratio=(1.3, 1.7)), key=lambda b: (round((b[1] + b[3]) / 2 / 400), b[0]))
    bs = [b for b in bs if b[1] > 500]
    assert len(bs) == 6, bs
    for n, b in zip(ORDER, bs):
        j.add(C, [n], "HIT! MAGAZINE", "", hm.crop(tuple(int(v) for v in b)), "@nishitemplates")
    g = grid.load(D + "wishlist_Gaeul_idalshiro.jpg")
    j.add(C, ["ガウル"], "KMONSTAR", "2.0", g.crop(inset_frame(g, box(7, 0))), "@idalshiro")
    y = grid.load(D + "wishlist_Yujin_idalshiro.jpg")
    j.add(C, ["ユジン"], "QQ Music", "Membership", y.crop(inset_frame(y, box(3, 1))), "@idalshiro")
    q = grid.load(D + "QQ_random5_6cards.jpg")
    W, H = q.size
    j.add(C, ["ユジン"], "QQ Music", "2.0 ランダム 5", q.crop((int(W / 3), 0, int(W * 2 / 3), int(H / 2))), "@idalshiro")
    # Member set 2 の画像を Membership にコピー（Membership に画像のないメンバーだけ）
    have = {}
    for p in sorted(glob.glob(SP + "out/*.json")):
        if os.path.basename(p) == "revive_add.json":
            continue
        for e in json.load(open(p, encoding="utf-8"))["images"]:
            if e["collection"] == C and len(e["members"]) == 1 and e["source"] == "QQ Music" and e["credit"] != "@powerofablink":
                have[(e["members"][0], e["version"])] = e
    for n in ORDER:
        if (n, "Membership") not in have and (n, "Member set 2") in have and n != "ユジン":
            e = have[(n, "Member set 2")]
            j.add(C, [n], "QQ Music", "Membership", Image.open(CARDS + e["file"]), e["credit"])
    j.save()
