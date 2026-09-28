"""ELEVEN と LOVE DIVE：全体表と個別の表から、枠と画像を作り直す"""
from build2 import *

G = "グッズ｜"

# ---------- ELEVEN ----------
j = Job("eleven")
C = "ELEVEN"
overview(j, ENG + "01 - eleven/07-ive.JPG", C, [
    ((0, 1949), [("本体封入", "ver.1"), ("本体封入", "ver.2"), (G + "本体封入", "Poster"), ("POB", "ID Card"), ("POB", "Message Card"),
                 ("Starship Square", "1"), ("Starship Square", "2"), ("Ktown4U", ""), ("Soundwave", "1.0"), ("Yizhiyu", "1.0"),
                 ("Yizhiyu", "2.0"), ("Tower Records", ""), ("Shopee", ""), ("mymusictaste", "")]),
    ((1949, 3898), [("Soundwave ラキドロ", "2.0-1"), ("Soundwave ラキドロ", "2.0-2"), ("Soundwave ラキドロ", "2.0 POLA"),
                    ("Withdrama ラキドロ", "2.0-1"), ("Withdrama ラキドロ", "2.0-2"), ("Withdrama ラキドロ", "2.0 POLA"),
                    ("EVERLINE", "1.0"), ("Makestar", "1.0"), ("Withdrama", "3.0"), ("Wonderwall", ""), ("Soundwave", "3.0"),
                    ("EVERLINE", "2.0"), ("JoeunMusic", ""), ("Makestar", "2.0")]),
])
sheet6(j, ENG + "01 - eleven/10-daum cafe.JPG", C, "Daum Cafe", "")
for m in ORDER:
    j.add(C, [m], "Fansign Special", "")
j.save()

# ---------- LOVE DIVE ----------
j = Job("lovedive")
C = "LOVE DIVE"
overview(j, ENG + "02 - love dive/07-all.JPG", C, [
    ([693, 906, 1120, 1334, 1545, 1756],
     [("本体封入", "ver.1"), ("本体封入", "ver.2"), ("本体封入", "ver.3"), ("本体封入", "Heart Hologram Card"), (G + "POB", "Sticker"),
      (G + "本体封入", "Jewel ver. Photobook"), ("本体封入", "Jewel ver."), (G + "本体封入", "Jewel ver. 2cut Photo"),
      (G + "本体封入", "Jewel ver. Mini Folded Poster"), ("Jewel ver. POB", "6set Heart"), ("Jewel ver. POB", "9set MV"),
      ("Starship Square", "1"), ("Starship Square", "2"), ("Ktown4U", "1.0"), ("Tower Records", "1"), ("Tower Records", "2 POLA"),
      ("mymusictaste", ""), ("Soundwave", "1.0")]),
    ([2357, 2571, 2784, 2995, 3209, 3420],
     [("withmuu ラキドロ", "1.0-1"), ("withmuu ラキドロ", "1.0-2"), ("withmuu ラキドロ", "1.0 POLA"), ("Apple Music", ""),
      ("Namil Music", "1.0"), ("withmuu", "2.0"), ("Music Korea", ""), ("Soundwave", "2.0"),
      ("Soundwave ラキドロ", "3.0-1"), ("Soundwave ラキドロ", "3.0-2"), ("Soundwave ラキドロ", "3.0 POLA"), ("Beatroad", ""),
      ("Ktown4U", "2.0"), ("Namil Music", "2.0"), ("withmuu", "3.0"), ("MokketShop", ""), ("Soundwave", "4.0")]),
], y_from=0.06)
sheet6(j, ENG + "02 - love dive/09-daum cafe.jpg", C, "Daum Cafe", "")
for m in ORDER:
    j.add(C, [m], "Fansign Special", "")
j.save()
