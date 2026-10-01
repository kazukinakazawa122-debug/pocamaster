from build2 import *
import memlist as ml
import numpy as np
C = "IVE SECRET"
SS, LD, SW, WM, AM, MS = "Starship Square", " ラキドロ", "Soundwave", "withmuu", "Apple Music", "Makestar"
OFF = "オフラインイベント"
lab = [("本体封入", v) for v in ["Shh!", "Gasp!", "Psst!", "LOVED IVE", "Instant Photo Shh!", "Instant Photo Gasp!", "Instant Photo Psst!", "Digipack", "Evil Cupid"]]
lab += [("グッズ｜POB", "HMV Sticker"),
        (SS, "3TYPE 1"), (SS, "3TYPE 2"), (SS, "4TYPE"), (SS, "3+6 (A)"), (SS, "3+6 (B)"), (SS, "LOVED IVE"), (SS, "Digipack"),
        (SW, "1.0"), (WM, "1.0"), (AM, "1.0"), (MS, "1.0"), ("京东", ""),
        ("Tower Records", "A"), ("Tower Records", "Shibuya"), ("Sony Music", "B"), ("A!SMART", "C"), ("US Exclusive", ""), ("Target", ""),
        ("Barnes & Noble", ""), ("Music Korea", ""), (SW + LD, "2.0"), (SW + LD, "2.0 POLA"), (WM + LD, "2.0"), (WM + LD, "2.0 POLA"),
        ("OLIVE YOUNG" + LD, ""), ("Beatroad" + LD, "1.0"), ("Beatroad" + LD, "1.0 POLA"), (AM, "2.0"), (MS, "2.0"),
        ("Ktown4U", "STUDIO CHOOM"), ("Broadcast", ""), ("StarRiver", ""), ("hellolive", "1.0"), (WM, "3.0"), ("MusicArt", ""), ("HOTTRACKS", ""),
        (SW, "3.0"), (MS, "3.0"), (OFF, "9.23 TOKYO"), (OFF, "9.24 OSAKA"), (OFF, "10.12 TOKYO"), (OFF, "10.13 OSAKA"), (AM, "3.0"),
        (SW, "4.0"), (WM + LD, "4.0"), (WM + LD, "4.0 POLA"), (WM, "5.0"), ("Beatroad", "2.0"),
        (WM + LD, "6.0 Special HI-BYE-1"), (WM + LD, "6.0 Special HI-BYE-2"), (MS + LD, "4.0"), (MS + LD, "4.0 UNIT"),
        (SW, "5.0"), (OFF, "11.23 TOKYO"), (OFF, "11.24 OSAKA"), (AM, "4.0"), ("KMONSTAR", "1.0"), (WM, "7.0"), ("hellolive", "2.0"), ("NY Music", ""),
        ("KMONSTAR", "2.0"), (WM + LD, "8.0-1"), (WM + LD, "8.0-2"), (WM + LD, "8.0 POLA"), ("IDOLSHOP", ""),
        ("Yetimall" + LD, "-1"), ("Yetimall" + LD, "-2"), ("Yetimall" + LD, "POLA"), (MS, "5.0"),
        (AM + LD, "5.0-1"), (AM + LD, "5.0-2"), (AM + LD, "5.0 POLA"), (WM + LD, "9.0-1"), (WM + LD, "9.0-2"), (SW + LD, "6.0")]
UNIT = 61
_, tmpl, _ = ml.ordered(ROOT + ml.FILES[40])
assert len(tmpl) == len(lab) == 85, (len(tmpl), len(lab))
mems = [("ユジン", 40), ("ガウル", 41), ("レイ", 42), ("ウォニョン", 43), ("イソ", 44), ("リズ", 45)]
ims = {m: grid.load(ROOT + ml.FILES[i]) for m, i in mems}

# UNIT カードのペアを、同じ写真どうしで決める
def dh(img, n=16):
    w, h = img.size
    a = np.asarray(img.crop((w * .12, h * .12, w * .88, h * .88)).convert("L").resize((n + 1, n))).astype(int)
    return (a[:, 1:] > a[:, :-1]).flatten()
b = tuple(int(x) for x in tmpl[UNIT])
hs = {m: dh(ims[m].crop(b)) for m, _ in mems}
cand = sorted((int((hs[a] != hs[c]).sum()), a, c) for i, (a, _) in enumerate(mems) for c, _ in mems[i + 1:])
pair, used = {}, set()
for d, a, c in cand:
    if a in used or c in used: continue
    pair[a], pair[c] = c, a; used |= {a, c}; print("UNIT", a, c, d)

j = Job("secret")
done = set()
for m, _ in mems:
    for k, (bx, (s, v)) in enumerate(zip(tmpl, lab)):
        members = [m]
        if k == UNIT:
            members = sorted([m, pair[m]])
            if tuple(members) in done: continue
            done.add(tuple(members))
        j.add(C, members, s, v, ims[m].crop(tuple(int(x) for x in bx)), "@LILY_221019")

# 上の表にない種類（@powerofablink の表で見つけた。ID の透かしがあるので枠だけ足し、画像は使わない。2026-09-29）
EXTRA = [("MD", ""), ("IDOLSHOP", "POLA"), ("StarRiver", "2.0")] + [("QQ Music", str(n)) for n in range(1, 6)]  # QQ Music 6 は「QQ Music × Starship Square」の Christmas と同じ（本人、2026-10-01）
# @ri__chan94 のメンバー別・全員の表（Google ドライブ、2025-09 更新）で見つけた種類（2026-09-29）
# 「the stage」は「MusicArt」のこと（本人、2026-10-01）。the stage ラキドロ 1＝MusicArt（すでにある）、2＝MusicArt の全員のカード（下で全員 1 枠）。Krispy Kreme はトレカではない

for m, _ in mems:
    for s, v in EXTRA:
        j.add(C, [m], s, v)
j.add(C, ["全員"], "HOTTRACKS" + LD, "全員")
j.add(C, ["全員"], "MusicArt", "全員")
j.save()
