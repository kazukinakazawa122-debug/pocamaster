from build2 import *
import memlist as ml
C = "I've MINE"
G = "グッズ｜本体封入"
SS, LD, SW = "Starship Square", " ラキドロ", "Soundwave"
lab = [("本体封入", "Either Way (Pink ver.)"), ("本体封入", "Off The Record (Red ver.)"), ("本体封入", "Baddie (Gray ver.)"),
       (G, "Either Way POB Pink Photo"), (G, "Off The Record POB Red Photo"), (G, "Baddie POB Gray Photo"),
       ("本体封入", "PLVE ver."), ("本体封入", "LOVED IVE (White ver.)"), (G, "LOVED IVE POB Poster"), (G, "LOVED IVE POB Polaroid"),
       ("本体封入", "Digipack ver."), ("Broadcast", "LOVED IVE"), ("Broadcast", "Baddie"),
       (SS, "Digipack 6set"), (SS, "Digipack 6+3set"), (SS, "PB 3+1set"), (SS, "PB LOVED IVE"), (SS, "PB EW+OTR+BADDIE 1"), (SS, "PB EW+OTR+BADDIE 2"),
       ("Ktown4U", "1.0"), ("Namil Music", "1.0"), (SW, "1.0"), ("Kakao Gift", ""), ("withmuu", "1.0"), ("IDOUSTAGE", "1.0"),
       ("KMStation", "1.0"), ("mymusictaste", "1.0"), ("Tower Records", "1.0"), ("Tower Records", "Shibuya"), ("Apple Music", "1.0"),
       ("Namil Music", "2.0"), ("Ktown4U", "2.0"), ("Beatroad", ""),
       (SW + LD, "2.0-1"), (SW + LD, "2.0-2"), ("withmuu" + LD, "2.0-1"), ("withmuu" + LD, "2.0-2"), ("withmuu", "3.0"),
       ("KMStation", "2.0"), (SW, "3.0"), ("Taiwan", ""), (SW + LD, "4.0-1"), (SW + LD, "4.0-2"),
       ("Makestar", "1.0"), ("Apple Music", "2.0"), ("US Exclusive", ""), ("IDOUSTAGE", "2.0"), ("KMStation", "3.0"), ("withmuu", "4.0"),
       ("MusicArt", ""), ("HOTTRACKS", ""), ("mymusictaste", "2.0"), (SW, "5.0"),
       ("Namil Music", "3.0"), ("Japan Yokohama Live", "15th Day1"), ("Japan Yokohama Live", "16th Day2"), ("Hi-Touch", "18th・19th"),
       ("Tower Records", "2.0"), (SW, "6.0"), ("withmuu", "5.0"), ("withmuu" + LD, "6.0-1"), ("withmuu" + LD, "6.0-2"), ("withmuu" + LD, "6.0-3"),
       ("Makestar", "2.0"), ("Yizhiyu", "1.0"), (SW, "7.0 Busan"), (SW, "8.0 Daegu"), (SW, "9.0 Gwangju"), (SW, "10.0 Daejeon"),
       (SW, "11.0 Xmas"), ("KMStation", "4.0"), (SW, "12.0 Thailand"), ("mymusictaste", "3.0"), ("Yizhiyu", "2.0")]
BLUR = {70, 72, 73}
D = ENG + "I_VE MINE/"
_, tmpl, rows = ml.ordered(D + "06.JPG")
assert len(tmpl) == len(lab) == 74, (len(tmpl), len(lab))
j = Job("mine")
for mem, f in [("ガウル", "01.JPG"), ("ユジン", "02.JPG"), ("ウォニョン", "04.JPG"), ("レイ", "04(1).JPG"), ("リズ", "05.JPG"), ("イソ", "06.JPG")]:
    im = grid.load(D + f)
    for k, (b, (s, v)) in enumerate(zip(tmpl, lab)):
        j.add(C, [mem], s, v, None if k in BLUR else im.crop(tuple(int(x) for x in b)), "@reina831wy")
j.save()
