"""SHOW WHAT I AM の VIP Perks Japan（実物の写真の画面写真。本人が 2026-10-01 に入れた。pocamaster-images/新しい資料 2026-10-01/SHOW WHAT I AM VIP Perks Japan 追加分/）

- 2 段×3 列の 6 枚。並びは標準の順ではない：上段＝ユジン・ガウル・イソ、下段＝レイ・ウォニョン・リズ
  （顔ではなく、@idalshiro のメンバー別の表の同じ位置のカードと写真を突き合わせて決めた：0.87・0.76・0.61・0.63・0.82・0.69。リズは既存の SWIA VIP Perks Japan の画像と同じ写真 0.80）
- 画像のなかったリズ以外の 5 人に入れる。リズはいまの画像が小さければ入れ替える
- 表示 647 幅の座標 × 1284/647
"""
from PIL import Image
from build2 import *

D = ROOT + "新しい資料 2026-10-01/SHOW WHAT I AM VIP Perks Japan 追加分/"
k = 1284 / 647
ORDER = ["ユジン", "ガウル", "イソ", "レイ", "ウォニョン", "リズ"]
BOX = [(40, 410, 210, 665), (233, 407, 402, 662), (421, 407, 604, 662), (15, 688, 196, 972), (220, 697, 402, 985), (435, 692, 619, 980)]
if __name__ == "__main__":
    im = Image.open(D + "VIP_Perks_Japan_実物.png").convert("RGB")
    j = Job("zzzzzzzzzzzzzzzzz_swia_vip")
    for m, b in zip(ORDER, BOX):
        j.add("2nd WORLD TOUR 'SHOW WHAT I AM'", [m], "VIP Perks Japan", "", im.crop((int(b[0] * k) + 6, int(b[1] * k) + 6, int(b[2] * k) - 6, int(b[3] * k) - 6)), "本人の写真")
    j.save()
