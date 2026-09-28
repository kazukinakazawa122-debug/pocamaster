from build2 import *
import memlist as ml
C = "IVE EMPATHY"
SS, LD, SW, WM, AM, MS = "Starship Square", " ラキドロ", "Soundwave", "withmuu", "Apple Music", "Makestar"
album = [("本体封入", "Me ver."), ("本体封入", "You ver."), ("本体封入", "And us ver."), ("本体封入", "LOVED IVE ver."),
         ("本体封入", "PLVE"), ("本体封入", "Digipack"), ("MD", ""), ("Broadcast", "1.0"), ("Broadcast", "2.0")]
pre = [(SS, "3TYPE 1"), (SS, "3TYPE 2"), (SS, "4TYPE"), (SS, "3+6 (A)"), (SS, "3+6 (B)"), (SS, "LOVED IVE"), (SS, "Digipack"),
       (SW, "1.0"), (WM, "1.0"), (AM, "1.0"), (MS, "1.0"), ("StarRiver", "1.0"),
       ("mymusictaste", "1.0"), (WM, "2.0 Live Studio Choom"), ("StarRiver", "2.0"), ("Tower Records", "A"), ("Tower Records", "Shibuya"),
       ("Sony Music", "1.0 B"), ("A!SMART", "C"), (AM, "2.0"), (WM + LD, "3.0"), (WM + LD, "3.0 POLA"), (SW + LD, "2.0"), (SW + LD, "2.0 POLA"),
       (MS, "2.0"), ("MusicArt", ""), ("HOTTRACKS", ""), ("Ktown4U", ""), (WM, "4.0"), (SW, "3.0"), (MS, "3.0"),
       (WM + LD, "5.0"), (WM + LD, "5.0 POLA"), ("US Exclusive", ""), (SW + LD, "4.0"), (SW + LD, "4.0 POLA"),
       (SW, "5.0"), ("IDOUSTAGE" + LD, "1.0"), ("IDOUSTAGE" + LD, "1.0 POLA"), (AM, "3.0"), (WM, "6.0"), ("mymusictaste", "2.0"),
       (SW, "6.0"), (AM, "4.0"), ("オフラインイベント", "TOKYO"), ("オフラインイベント", "OSAKA"), ("Sony Music", "2.0"), (SW, "7.0"),
       ("K-MONSTAR", "Taiwan"), ("K-MONSTAR", "Taiwan POLA"), (SW + LD, "8.0 IVE SCOUT-1"), (SW + LD, "8.0 IVE SCOUT-2"),
       ("StarRiver", "3.0"), ("IDOUSTAGE", "2.0"), (MS, "4.0 Shanghai"), (MS, "4.0 Shanghai カフェ店長 ver.")]
lab = album + pre
_, t, rows = ml.ordered(ROOT + ml.FILES[36])
tmpl = [t[i] for i in [0, 1, 2, 3, 6, 7, 8, 9, 10]] + t[11:]
assert len(tmpl) == len(lab) == 65, (len(tmpl), len(lab))
BLUR = {len(lab) - 3, len(lab) - 2, len(lab) - 1}
j = Job("empathy")
for mem, i in [("レイ", 34), ("ユジン", 35), ("ガウル", 36), ("イソ", 37), ("ウォニョン", 38), ("リズ", 39)]:
    im = grid.load(ROOT + ml.FILES[i])
    for k, (b, (s, v)) in enumerate(zip(tmpl, lab)):
        j.add(C, [mem], s, v, None if k in BLUR else im.crop(tuple(int(x) for x in b)), "@LILY_221019")
j.save()
