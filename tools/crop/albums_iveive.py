from build2 import *
import memlist as ml
C = "I've IVE"
SS, LD = "Starship Square", " ラキドロ"
head = [("本体封入", v) for v in ["I ver.", "V ver.", "E ver.", "Jewel Case", "Special Edition"]]
head += [("Ktown4U", ""), (SS + " Album", "1"), (SS + " Album", "2"), (SS + " Jewel Case", ""), (SS + " Set", ""),
         (SS + " Special", ""), ("Mokket", ""), ("Soundwave", ""), ("Soundwave" + LD, "1"), ("Soundwave" + LD, "2"), ("Soundwave" + LD, "3"),
         ("Soundwave FC", "")]
wm = [("withmuu" + LD, "1"), ("withmuu" + LD, "2"), ("withmuu" + LD, "3"), ("withmuu FC", ""), ("mymusictaste", ""),
      ("Tower Records", "1"), ("Tower Records", "2")]
tail = [("Naver Live", ""), ("HOTTRACKS", ""), ("Makestar", ""), ("Apple Music", ""), ("Beatroad", ""),
        ("Broadcast", "1"), ("Broadcast", "2"), ("Broadcast", "3")]
std = head + [("Soundwave FC2", ""), ("MusicArt", "")] + wm + [("Namil Music", ""), ("StarRiver", ""), ("StarRiver FC", "")] + tail + [("Fancall", "")]
rei = head + [("Namil Music", ""), ("MusicArt", "")] + wm + [("StarRiver FC", "")] + tail
print(len(std), len(rei))
j = Job("iveive")
for mem, i in [("ガウル", 0), ("ユジン", 1), ("レイ", 2), ("ウォニョン", 3), ("リズ", 4), ("イソ", 5)]:
    lab = rei if mem == "レイ" else std
    im, seq, rows = ml.ordered(ROOT + ml.FILES[i])
    if len(seq) != len(lab):
        print("SKIP", mem, len(seq)); continue
    for b, (s, v) in zip(seq, lab):
        j.add(C, [mem], s, v, im.crop(tuple(int(x) for x in b)), "@powerofablink")
j.save()
