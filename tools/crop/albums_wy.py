"""ウォニョン個人（全体表 IMG_5528 の番号 → 枠）"""
import json
import numpy as np
from build2 import *

C = "Wonyoung Solo｜ウォニョン個人"
seq = json.load(open(SP + "wy_seq.json"))
W = float(np.median([b[2] - b[0] for b in seq[5:]]))
H = float(np.median([b[3] - b[1] for b in seq[5:]]))
lab = {}
def put(start, src, vers):
    for i, v in enumerate(vers):
        lab[start + i] = (src, v)
n = lambda k, p="": [f"{p}{i}" for i in range(1, k + 1)]
put(5, "Kirsh", n(5, "21AW "))
put(10, "Kirsh", n(3, "22SS "))
put(13, "Kirsh", ["22AW"])
put(14, "Kirsh", n(9, "21AW Black Friday "))
put(23, "Hapa Kristin", n(3, "One & Only Brown ") + n(3, "One & Only Gray ") + n(3, "Secretive Beige ") + n(3, "Secretive Olive ")
    + ["2.0 A to Z", "2.0 Dewy", "2.0 Sugar High"] + n(3, "3.0 A set ") + n(3, "3.0 B set ") + n(4, "4.0 "))
put(48, "innisfree", n(2, "set A ") + n(2, "set B ") + ["Music Bank"])
put(53, "SK Telecom", n(3))
put(56, "GOSPHERES", n(3, "23SS "))
put(59, "EIDER", n(4))
put(67, "AMUSE", n(2, "1.0 Foundation ") + ["1.0 Lip Tint", "1.0 Tokyo Cherry"] + n(2, "2.0 Cushion ") + ["2.0 Lip Tint"])

j = Job("wonyoung")
im = grid.load(ENG + "#wonyoung/IMG_5528.JPG")
for i, b in enumerate(seq):
    if i not in lab:
        continue
    box = (int(b[0]), int(b[1]), int(b[0] + W), int(b[1] + H))  # 大きさをそろえる（左上を基準）
    j.add(C, ["ウォニョン"], lab[i][0], lab[i][1], im.crop(box))
j.save()

# Music Bank MC 生放送入場限定（IMG_9176：6 列 × 4 段、日付順）
S = "Music Bank MC 生放送入場限定"
dates = ["220513", "220520", "220527", "220603", "220610", "220617", "220624", "220701", "220708", "220715", "220722", "220729",
         "220812", "220819", "220923", "220930", "221007", "221021", "221028", "221118", "221125", "221209", "230113", "名刺"]
im = grid.load(ENG + "#wonyoung/musicbank/IMG_9176.JPG")
Wd, Hd = im.size
xs = [.141, .283, .430, .572, .715, .861]
ys = [.206, .418, .629, .835]
k = 0
for fy in ys:
    for fx in xs:
        cell = im.crop((int((fx - .07) * Wd), int((fy - .1) * Hd), int((fx + .07) * Wd), int((fy + .085) * Hd)))
        j.add(C, ["ウォニョン"], S, dates[k], trim(cell))
        k += 1
j.save()
