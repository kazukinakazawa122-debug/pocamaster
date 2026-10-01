"""I've MINE の足りない画像（本人が 2026-10-01 にフォルダへ入れた。pocamaster-images/新しい資料 2026-10-01/I've MINE 追加分/）

- Soundwave_ファンサイン_Malaysia_Rei.png：レイの Soundwave ファンサイン Malaysia（画面写真。カードの位置を画面から見つけた）
- Taiwan2_全員.jpg：Taiwan 2 の 6 人（2 段×3 列：ユジン・ガウル・レイ／ウォニョン・リズ・イソ）。既存の Taiwan 2 の画像と同じ写真で並びを確認（ユジン・ガウル・ウォニョン・リズ 0.61〜0.83）。6 人全員をこの写真に入れ替える（本人）
- 会場限定特典_大阪城ホール_2-7_reina831wy.jpg：「JAPAN OSAKA LIVE TOUR 会場限定特典 大阪城ホール 2月7日」6 人（ガウル・ユジン・レイ／ウォニョン・リズ・イソ）。
  アプリの「Sony Music Japan 2-3」は名前がちがい、これが正しい（本人）→ 枠を「会場限定特典 大阪城ホール｜2/7」にして、6 人ともこの画像にする
  （既存の Sony Music Japan 2-3 の画像と同じ写真：ガウル 0.75・ユジン 0.70・レイ 0.69・リズ 0.85）
"""
import numpy as np
from PIL import Image
import grid
from build2 import *

D = ROOT + "新しい資料 2026-10-01/I've MINE 追加分/"
C = "I've MINE"
OSAKA = "会場限定特典 大阪城ホール"
M = ["ユジン", "ガウル", "レイ", "ウォニョン", "リズ", "イソ"]
if __name__ == "__main__":
    j = Job("zzzzzzzz_mine_add")
    mal = Image.open(D + "Soundwave_ファンサイン_Malaysia_Rei.png").convert("RGB")
    j.add(C, ["レイ"], "Soundwave ファンサイン", "Malaysia", mal.crop((222, 748, 1075, 1998)), "本人の写真")
    t = Image.open(D + "Taiwan2_全員.jpg").convert("RGB")
    cs = [(52, 516), (519, 976), (980, 1437)]; rs = [(36, 742), (748, 1446)]
    for i, m in enumerate(M):
        (x0, x1), (y0, y1) = cs[i % 3], rs[i // 3]
        j.add(C, [m], "Taiwan", "2", t.crop((x0 + 3, y0 + 3, x1 - 3, y1 - 3)), "本人の写真")
    o = grid.load(D + "会場限定特典_大阪城ホール_2-7_reina831wy.jpg")
    bs = sorted((b for b in grid.card_boxes(o, min_w=0.1, max_w=0.25, ratio=(1.3, 1.7)) if b[1] > 350), key=lambda b: (round((b[1] + b[3]) / 2 / 600), b[0]))
    assert len(bs) == 6
    for m, b in zip(["ガウル", "ユジン", "レイ", "ウォニョン", "リズ", "イソ"], bs):
        j.add(C, [m], OSAKA, "2/7", o.crop(tuple(int(v) for v in b)), "@reina831wy")
    j.save()
