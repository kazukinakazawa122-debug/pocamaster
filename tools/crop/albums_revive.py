from build2 import *
import memlist as ml
C = "REVIVE+"
G = "グッズ｜"
SS, LD = "Starship Square", " ラキドロ"
lab = [("本体封入", v) for v in ["BANGERS", "CHALLENGERS", "SPOILERS", "LOVED IVE"]]
lab += [(G + "本体封入", "Postcard BANGERS"), (G + "本体封入", "Postcard CHALLENGERS"),
        ("本体封入", "Digipack"), ("本体封入", "PETIT-IVE"), ("MD", ""),
        (SS, "3TYPE"), (SS, "LOVED IVE"), (SS, "Digipack"), ("京东", "1.0"), ("withmuu", "1.0"), ("Apple Music", "1.0"),
        ("Music Korea", "1.0"), ("Kakao Talk", ""), ("US Exclusive", ""), ("Target", ""), ("B&N", ""), ("Ktown4U", "1.0"),
        ("Tower Records", "A"), ("Tower Records", "Shibuya"), ("Sony Music", "B"), ("A!SMART", "C"), ("Soundwave", "1.0"),
        ("Makestar", "1.0"), ("MusicArt", "1.0"), ("ARTBOX", ""), ("Broadcast", "BANG BANG"), ("withmuu", "2.0 Killing Voice"),
        ("withmuu" + LD, "3.0"), ("withmuu" + LD, "3.0 POLA"),
        ("OLIVE YOUNG" + LD, ""), ("Music Korea", "2.0"), ("HOTTRACKS", ""), ("Showcase", ""), ("Makestar", "2.0"),
        ("Apple Music", "2.0"), ("Broadcast", "BLACK HOLE"), ("withmuu", "4.0"), ("NY Music", "1.0"), ("QQ音乐" + LD, ""),
        ("Beatroad", "1.0"), ("Apple Music", "3.0"),
        ("withmuu" + LD, "5.0-1"), ("withmuu" + LD, "5.0-2"), ("Soundwave" + LD, "2.0"), ("Soundwave" + LD, "2.0 POLA"),
        ("MusicArt" + LD, "2.0"), ("MusicArt" + LD, "2.0 POLA"), ("オフラインイベント", "4.11 TOKYO"), ("オフラインイベント", "4.12 OSAKA"),
        ("KMStation", "1.0"), ("SWIA OSAKA exclusive", "4.18"), ("SWIA OSAKA exclusive", "4.19"), ("オフラインイベント", "4.29 TOKYO"),
        ("withmuu" + LD, "6.0"), ("withmuu" + LD, "6.0 POLA"), ("withmuu", "7.0"), ("KMStation", "2.0"), ("KMStation", "3.0"),
        ("Makestar", "3.0"), ("Ktown4U", "2.0"), ("京东", "2.0"), ("KMStation", "4.0"), ("Music Korea", "3.0"), ("Ktown4U", "3.0"),
        ("withmuu", "8.0"), ("withmuu" + LD, "9.0"), ("withmuu" + LD, "9.0 POLA"), ("withmuu", "10.0"),
        ("Ktown4U" + LD, "4.0"), ("Ktown4U" + LD, "4.0 POLA"), ("Soundwave" + LD, "3.0"), ("Soundwave" + LD, "3.0 POLA"),
        ("Yetimall", "1.0"), ("Yetimall", "2.0"), ("Makestar" + LD, "4.0"), ("Makestar" + LD, "4.0 POLA"), ("KMONSTAR", "1.0"),
        ("NY Music" + LD, "2.0"), ("NY Music" + LD, "2.0 POLA")]
NOIMG = {61, 65}
print(len(lab))
j = Job("revive")
for mem, i in [("イソ", 53), ("リズ", 54), ("ウォニョン", 55), ("レイ", 56), ("ユジン", 57), ("ガウル", 58)]:
    im, seq, rows = ml.ordered(ROOT + ml.FILES[i])
    if len(seq) == 84:
        del seq[8]  # PETIT-IVE キーリングが検出された
    if len(seq) != len(lab):
        print("SKIP", mem, len(seq)); continue
    for k, (b, (s, v)) in enumerate(zip(seq, lab)):
        j.add(C, [mem], s, v, None if k in NOIMG else im.crop(tuple(int(x) for x in b)), "@LILY_221019")
# @hallojisoo の一覧（Google ドライブ、2026-08-23 更新）で見つけた種類。枠だけ（2026-09-29）
# QQ Music 1〜5・Shatter Card・POP-UP は、画像のある「QQ Music 2.0 ランダム 1〜6」などと同じカードなので枠を作らない（本人、2026-10-01。removed.csv）
EXTRA = [("本体封入", "Vinyl"), ("Melon Live", ""), ("QQ Music", "Membership"),
         ("HIT! MAGAZINE", ""), ("KMONSTAR", "2.0")]
for mem in ["イソ", "リズ", "ウォニョン", "レイ", "ユジン", "ガウル"]:
    for s, v in EXTRA:
        j.add(C, [mem], s, v)
j.save()
