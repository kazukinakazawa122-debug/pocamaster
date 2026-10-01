"""IVE SECRET の withmuu ラキドロ 8.0 POLA の実物の写真（本人が 2026-10-01 に入れた。pocamaster-images/新しい資料 2026-10-01/IVE SECRET withmuu 8.0 POLA 追加分/）

- 「withmuu ラキドロ 4.0-3」は名前がまちがいで、withmuu 8.0 のポラロイド（本人）→ 4.0-3 の枠 6 を消す（merge.py の DROP_SLOT）
  （4.0-3 の画像はアプリの 8.0 POLA と同じ写真だった）
- 8.0 POLA の実物の写真 3 枚（ウォニョン＝「PRETTY RUDE」・レイ＝「I'm lovely」・ガウル＝「Gasp」。ファイル名は本人の対応表ではなく、アプリの既存 8.0 POLA の画像と Tシャツの文字が同じことで確認）。
  いまの画像（約 120px）より大きいので入れ替える（576〜768px）
- 画面写真の位置は画面を見て決めた（表示 647 幅の座標 × 1284/647）
"""
from PIL import Image
from build2 import *

D = ROOT + "新しい資料 2026-10-01/IVE SECRET withmuu 8.0 POLA 追加分/"
k = 1284 / 647
FILES = [("POLA_PRETTY_RUDE_ウォニョン.png", "ウォニョン", (113, 411, 500, 982)), ("POLA_I'm_lovely_レイ.png", "レイ", (197, 470, 493, 897)), ("POLA_Gasp_ガウル.png", "ガウル", (138, 440, 508, 984))]
if __name__ == "__main__":
    j = Job("zzzzzzzzzzzzz_secret_pola")
    for f, who, b in FILES:
        im = Image.open(D + f).convert("RGB")
        j.add("IVE SECRET", [who], "withmuu ラキドロ", "8.0 POLA", im.crop(tuple(int(v * k) for v in b)), "本人の写真")
    j.save()
