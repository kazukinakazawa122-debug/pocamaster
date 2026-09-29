from build2 import *
import memlist
F = lambda i: ROOT + memlist.FILES[i]
C = "IVE SWITCH"
SS, LD, FS = "Starship Square", "ラキドロ", "ファンサイン"
lab = [("本体封入", v) for v in ["ON", "OFF", "SPIN-OFF", "LOVED IVE", "Digipack", "PLVE", "Lenticular"]]
lab += [(SS, "1"), (SS, "2"), (SS, "LOVED IVE"), (SS, "Digipack"), (SS, "Set 1"), (SS, "Set 2"), (SS, "Set 3"),
        ("A!SMART", ""), ("Apple Music", ""), ("KakaoTalk", ""), ("Makestar", ""), ("Music Korea", ""), ("mymusictaste", ""),
        ("Sony Music", ""), ("Soundwave", ""), ("StarRiver", ""), ("Tower Records", ""), ("withmuu", "")]
for v in ["1.0", "2.0", "4.0", "5.0"]:
    lab += [("Soundwave " + LD, v + "-1"), ("Soundwave " + LD, v + "-2")]
lab += [("Music Korea " + LD, "1"), ("Music Korea " + LD, "2"), ("Makestar " + LD, "1"), ("Makestar " + LD, "2")]
for v in ["1.0", "2.0", "3.0"]:
    lab += [("withmuu " + LD, v + "-1"), ("withmuu " + LD, v + "-2")]
lab += [("Apple Music " + FS, v) for v in ["1.0", "2.0", "3.0"]]
lab += [("Soundwave " + FS, v) for v in ["1.0", "2.0", "Hong Kong", "Manila", "Jakarta"]]
lab += [("mymusictaste " + FS, ""), ("Tower Records " + FS, ""), ("Makestar " + FS, "1.0"), ("Makestar " + FS, "2.0"),
        ("withmuu " + FS, "1.0"), ("withmuu " + FS, "2.0")]
lab += [("Yizhiyu " + FS, v) for v in ["1.0", "2.0", "3.0", "4.0"]]
lab += [("StarRiver " + FS, "1.0"), ("StarRiver " + FS, "2.0"), ("Japan " + FS, "Tokyo"), ("Japan " + FS, "Osaka"),
        ("LINE FRIENDS トレカ", "1"), ("LINE FRIENDS トレカ", "2"), ("LINE FRIENDS 特典", "1"), ("LINE FRIENDS 特典", "2"),
        ("OSAKA イベント", ""), ("Broadcast", "1週目"), ("Broadcast", "2週目")]
print(len(lab))
j = Job("switch")
files = dict(zip(["ガウル", "ユジン", "レイ", "ウォニョン", "リズ", "イソ"], [F(i) for i in range(67, 73)]))
import memlist as ml
for mem, p in files.items():
    im, seq, rows = ml.ordered(p)
    seq = seq[rows[0]:]  # 見出しの段を捨てる
    if len(seq) != len(lab):
        print("SKIP", mem, len(seq)); continue
    for b, (s, v) in zip(seq, lab):
        j.add(C, [mem], s, v, im.crop(tuple(int(x) for x in b)), "@yunahsrem")
# ラキドロのポラ（@LILY_221019 の一覧 ver.9 で見つけた。アプリにポラが 1 枚もなかった。番号は LILY さんの表のまま。枠だけ、2026-09-29）
POLA = [("Soundwave ラキドロ", "2.0 POLA"), ("withmuu ラキドロ", "2.0 POLA"), ("Music Korea ラキドロ", "2.0 POLA"),
        ("Soundwave ラキドロ", "4.0 POLA"), ("withmuu ラキドロ", "5.0 POLA"), ("Makestar ラキドロ", "4.0 POLA"),
        ("withmuu ラキドロ", "6.0 POLA"), ("Soundwave ラキドロ", "6.0 POLA"), ("Soundwave ラキドロ", "9.0 POLA"),
        ("Soundwave ラキドロ", "11.0 POLA")]
for mem in files:
    for s, v in POLA:
        j.add(C, [mem], s, v)
j.save()
