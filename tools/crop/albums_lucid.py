from build2 import *
import memlist as ml
C = "LUCID DREAM"
G = "グッズ｜店舗特典"
UNIT = {"ガウル": "レイ", "レイ": "ガウル", "ユジン": "イソ", "イソ": "ユジン", "ウォニョン": "リズ", "リズ": "ウォニョン"}
P419 = {"ユジン": "ガウル", "ガウル": "ユジン", "レイ": "ウォニョン", "ウォニョン": "レイ", "イソ": "リズ", "リズ": "イソ"}
lab = [("本体封入", "初回生産限定盤 I"), ("本体封入", "初回生産限定盤 V"), ("本体封入", "初回生産限定盤 E"),
       ("本体封入", "通常盤 ユニットトレカ 1", UNIT), ("本体封入", "通常盤 ユニットトレカ 2", UNIT),
       ("本体封入", "メンバーソロジャケット盤"), ("本体封入", "期間生産限定盤"), ("本体封入", "会場限定盤"),
       ("A!SMART", "A"), ("タワレコ", "B"), ("HMV", "C"), ("Sony Music Shop", "1.0 clear pc"), ("タワレコ", "Shibuya（限定抽選）"),
       ("東京ドーム公演開催記念", "期間限定特典"), ("Sony Music Shop", "2.0 ラキドロ"), ("全国ラキドロ", ""), ("タワレコ", "online ラキドロ"),
       ("オフラインイベント", "4.11 TOKYO"), ("オフラインイベント", "4.12 OSAKA"), ("SWIA OSAKA exclusive", "4.18"),
       ("SWIA OSAKA exclusive", "4.19-1", P419), ("SWIA OSAKA exclusive", "4.19-2", P419), ("オフラインイベント", "4.29 TOKYO"),
       ("SWIA TOKYO exclusive", "6.24-1"), ("SWIA TOKYO exclusive", "6.24-2"), ("オフラインイベント", "7.5 TOKYO"),
       ("オフラインイベント", "8.30 OSAKA"), ("オフラインイベント", "8.31 TOKYO"),
       (G, "タワレコ スペシャルフライヤー"), (G, "HMV the music & movie master")]
j = Job("lucid")
done_pairs = set()
for mem, i in [("レイ", 61), ("ユジン", 62), ("ガウル", 63), ("ウォニョン", 64), ("イソ", 65), ("リズ", 66)]:
    im, seq, rows = ml.ordered(ROOT + ml.FILES[i])
    seq = list(seq)
    if len(seq) == 29:
        seq.insert(22, None)  # 白い 4.29 TOKYO のカードが見つからなかった
    if len(seq) != len(lab):
        print("SKIP", mem, len(seq)); continue
    for b, l in zip(seq, lab):
        s, v = l[0], l[1]
        members = [mem]
        if len(l) == 3:
            members = sorted([mem, l[2][mem]])
            if (s, v, tuple(members)) in done_pairs:
                continue
            done_pairs.add((s, v, tuple(members)))
        j.add(C, members, s, v, None if b is None else im.crop(tuple(int(x) for x in b)), "@LILY_221019")
j.save()
