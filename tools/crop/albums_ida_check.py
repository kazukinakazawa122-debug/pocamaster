"""本人が確認ページで「ない」とした @idalshiro の表のカード（メンバー別）を、ラベルに合わせて入れる（2026-09-30〜）

- 確認ページ：public/_review/<メンバー>.html（Git には入れない）。「ない」の番号は review_<メンバー>.json に書く
- 番号 → (コレクション, 入手元, バージョン, 扱い) はラベル（表の見出しのアルバム名・カードの下の文字）を目で読んで決めた
  - "have"：アプリに同じ枠がある。そのメンバーの枠に画像がなければ、この画像を入れる
  - "new"：アプリにない種類。6 人分の枠を足し、画像はそのメンバーの分だけ
  - "skip"：入れない（ユニットのカードで相手がわからない・すでにユニットの枠がある など）
- @idalshiro の 3 ページ目（日本盤）は作者が全部に「BOYCOTT!」の印を押しているので、画像は使わない（枠だけ）
- StarRiver は店の透かしがあるので画像は使わない（今までと同じ）
- ラベルの略語：SW=Soundwave、WM=withmuu、LD=ラキドロ、MKS=Makestar、SR=StarRiver、APPMU=Apple Music、YZY=Yizhiyu、
  KMS=KMStation、SSQ=Starship Square。グループのラベル（例「SOUNDWAVE LD 3」が 5 枚）は、表の左から 1, 2, 3… と番号をつけた
"""
import csv, glob, io, json, os
import grid
from build2 import *

D = ROOT + "_nonalbum/idalshiro/"
MEMBERS = ["ユジン", "ガウル", "レイ", "ウォニョン", "リズ", "イソ"]
SW, WM, SWL, WML = "Soundwave", "withmuu", "Soundwave ラキドロ", "withmuu ラキドロ"
H, N, X = "have", "new", "skip"

# イソ（review_leeseo.json の番号 → ラベル）
LEESEO = {
    4: ("ELEVEN", "POB", "ID Card", H),
    9: ("LOVE DIVE", "Fansign Special", "", H),
    10: ("LOVE DIVE", "Fansign Special", "2", N),
    13: ("LOVE DIVE", WML, "1.0-1", H),
    16: ("LOVE DIVE", "Fansign", "", N),
    17: ("LOVE DIVE", "Tower Records", "2 POLA", H),
    18: ("After LIKE", "本体封入", "ver.2", H),
    20: ("After LIKE", "Jewel ver. POB", "6+3set", H),
    23: ("After LIKE", WML, "2.0-2", H),
    24: ("After LIKE", SWL, "2.0-2", H),
    26: ("After LIKE", "Tower Records", "2", H),
    27: ("After LIKE", "TOU", "WINNER", N),
    30: ("After LIKE", "Broadcast", "After ver.", H),
    31: ("After LIKE", "Broadcast", "3", X),  # 2 人以上のカード（相手を顔で決めることになるので入れない）
    33: ("I've IVE", "Vinyl", "", N),
    34: ("I've IVE", "US Exclusive", "", X),  # 2 人以上のカード（相手を顔で決めることになるので入れない）
    37: ("I've IVE", "Naver Live", "", H),
    38: ("I've IVE", "Naver Live", "2", X),  # 2 人以上のカード（相手を顔で決めることになるので入れない）
    43: ("I've MINE", "Broadcast", "Baddie", H),
    45: ("I've MINE", "Starship Square", "PB LOVED IVE", H),
    46: ("I've MINE", "KMStation", "1.0", H),
    52: ("I've MINE", SWL, "3-2", X),  # 2 人以上のカード（相手を顔で決めることになるので入れない）
    53: ("I've MINE", SWL, "3-3", X),  # 2 人以上のカード（相手を顔で決めることになるので入れない）
    56: ("I've MINE", "withmuu", "4.0", H),
    57: ("I've MINE", "Soundwave ファンサイン", "Singapore", N),
    61: ("I've MINE", "Soundwave ファンサイン", "Malaysia", N),
    62: ("I've MINE", "Sony Music Japan", "2-1", N),
    63: ("I've MINE", "Sony Music Japan", "2-2", N),
    64: ("I've MINE", "Sony Music Japan", "2-4", N),
    65: ("I've MINE", "Sony Music Japan", "2-5", N),
    66: ("I've MINE", "A!SMART ファンサイン", "", N),
    69: ("I've MINE", "Yizhiyu", "3.0", N),
    68: ("IVE SWITCH", "本体封入", "SPIN-OFF", H),
    70: ("IVE SWITCH", "Tower Records", "2", N),
    72: ("IVE SWITCH", SWL, "1.0-3", N),
    73: ("IVE SWITCH", WML, "1.0-2", H),
    74: ("IVE SWITCH", WML, "1.0-3", N),
    76: ("IVE SWITCH", SWL, "2.0-3", N),
    77: ("IVE SWITCH", WML, "3.0-3", N),
    79: ("IVE SWITCH", WML, "4.0-3", N),
    81: ("IVE SWITCH", "Makestar ラキドロ", "3", N),
    83: ("IVE SWITCH", WML, "4.0（2 組目）-3", N),  # 表のラベルも「WITHMUU LD 4」（2 回目）
    84: ("IVE SWITCH", SWL, "3.0-1", X),  # 2 人以上のカード（相手を顔で決めることになるので入れない）
    85: ("IVE SWITCH", SWL, "3.0-2", X),  # 2 人以上のカード（相手を顔で決めることになるので入れない）
    86: ("IVE SWITCH", SWL, "3.0-3", X),  # 2 人以上のカード（相手を顔で決めることになるので入れない）
    87: ("IVE SWITCH", SWL, "3.0-4", X),  # 2 人以上のカード（相手を顔で決めることになるので入れない）
    88: ("IVE SWITCH", SWL, "3.0-5", X),  # 2 人以上のカード（相手を顔で決めることになるので入れない）
    90: ("IVE SWITCH", SWL, "4.0-3", N),
    91: ("IVE SWITCH", "TOKYO DOME 限定", "9/4", X),  # 2 人のカード。ユニットの枠がある
    92: ("IVE SWITCH", "TOKYO DOME 限定", "9/5", X),
    93: ("IVE SWITCH", SWL, "5.0-3", N),
    94: ("IVE SWITCH", "Yizhiyu ファンサイン", "2.0", H),
    96: ("IVE EMPATHY", "MD", "", H),
    97: ("IVE EMPATHY", "Starship Square", "3TYPE 1", H),
    106: ("IVE EMPATHY", "StarRiver", "1.0", H),
    111: ("IVE EMPATHY", "StarRiver", "2.0", H),
    112: ("IVE EMPATHY", "Makestar", "2.0", H),
    113: ("IVE EMPATHY", "withmuu", "2.0 Live Studio Choom", H),
    114: ("IVE EMPATHY", "Makestar", "3.0", H),
    121: ("IVE EMPATHY", SWL, "2.0-2", N),
    122: ("IVE EMPATHY", "オフラインイベント", "TOKYO 2", N),
    124: ("IVE EMPATHY", "StarRiver", "2.0（2 枚目）", N),
    125: ("IVE EMPATHY", "Soundwave", "4.0（2 枚目）", N),
    126: ("IVE EMPATHY", "K-MONSTAR", "Taiwan POLA", H),
    127: ("IVE EMPATHY", "Makestar", "4.0 Shanghai", H),
    128: ("IVE EMPATHY", "Makestar", "4.0 Shanghai 3", N),
    129: ("IVE SECRET", "MD", "", H),
    131: ("IVE SECRET", "Starship Square", "Digipack", H),
    134: ("IVE SECRET", "Apple Music", "1.0", H),
    136: ("IVE SECRET", "Tower Records", "Shibuya", H),
    137: ("IVE SECRET", "Sony Music", "B", H),
    138: ("IVE SECRET", "Mukor", "", N),
    139: ("IVE SECRET", "OLIVE YOUNG ラキドロ", "", H),
    144: ("IVE SECRET", "MusicArt", "", H),
    145: ("IVE SECRET", "Makestar", "3.0", H),
    146: ("IVE SECRET", "オフラインイベント", "9.23 TOKYO", H),
    147: ("IVE SECRET", "QQ Music", "1", H),
    148: ("IVE SECRET", "QQ Music", "2", H),
    149: ("IVE SECRET", "QQ Music", "3", H),
    150: ("IVE SECRET", "QQ Music", "4", H),
    152: ("IVE SECRET", WML, "2.0", H),
    153: ("IVE SECRET", WML, "2.0 POLA", H),
    157: ("IVE SECRET", "Shanghai", "WINNER", N),
    159: ("IVE SECRET", "KMONSTAR", "2.0", H),
    163: ("IVE SECRET", WML, "5.0-2", N),
    164: ("IVE SECRET", "QQ Music × Starship Square", "Christmas", N),
    165: ("IVE SECRET", "IDOLSHOP", "", H),
    167: ("IVE SECRET", WML, "4.0-3", N),
    173: ("REVIVE+", "本体封入", "MINI MINI", H),
    175: ("REVIVE+", "Mukor", "", N),
    180: ("REVIVE+", "QQ Music", "Member set 2", N),
    181: ("REVIVE+", "QQ Music", "2.0 ランダム 1", N),
    182: ("REVIVE+", "QQ Music", "2.0 ランダム 2", N),
    183: ("REVIVE+", "QQ Music", "2.0 ランダム 3", N),
    184: ("REVIVE+", "QQ Music", "2.0 ランダム 4", N),
    185: ("REVIVE+", "QQ Music", "2.0 ランダム 5", N),
    186: ("REVIVE+", "QQ Music", "2.0 ランダム 6", N),
    189: ("REVIVE+", SWL, "2.0", H),
    190: ("REVIVE+", "MusicArt ラキドロ", "2.0 POLA", H),
    194: ("REVIVE+", "KMONSTAR", "1.0", H),
    # 3 ページ目（日本盤）：画像は使わない
    198: ("ALIVE", "A!SMART", "ユニット 1", X),  # 2 人のカード。相手を顔で決めることになるので入れない
    199: ("ALIVE", "A!SMART", "ユニット 2", X),
    201: ("ALIVE", "オフラインイベント", "9/4 TOKYO ユニット 1", X),
    202: ("ALIVE", "オフラインイベント", "9/4 TOKYO ユニット 2", X),
    203: ("ALIVE", "オフラインイベント", "9/5 TOKYO ユニット 1", X),
    204: ("ALIVE", "オフラインイベント", "9/5 TOKYO ユニット 2", X),
    205: ("ALIVE", "オフラインイベント", "10/13 TOKYO ユニット", X),  # ユニットの枠がある
    206: ("ALIVE", "オフラインイベント", "10/13 TOKYO ユニット", X),
    207: ("ALIVE", "オフラインイベント", "10/14 OSAKA ユニット", X),
    208: ("ALIVE", "オフラインイベント", "10/14 OSAKA ユニット", X),
    209: ("Be Alright", "Sony Music ラキドロ", "", H),
    211: ("Be Alright", "オフラインイベント", "9.23 TOKYO", H),
    212: ("Be Alright", "オフラインイベント", "9.24 OSAKA", H),
    213: ("Be Alright", "オフラインイベント", "10.12 TOKYO", H),
    214: ("Be Alright", "オフラインイベント", "10.13 OSAKA", H),
    216: ("LUCID DREAM", "本体封入", "期間生産限定盤", H),
    217: ("LUCID DREAM", "本体封入", "DIVE 盤", N),
    218: ("LUCID DREAM", "タワレコ", "B", H),
    220: ("LUCID DREAM", "SWIA OSAKA exclusive", "4.19", X),  # 2 人のカード。ユニットの枠がある
}
PAGE3 = {"ALIVE", "Be Alright", "LUCID DREAM"}
NO_IMAGE_SOURCES = {"StarRiver"}
# 表の画像に店の透かし（BOYCOTT・中国語の印）がある → 枠だけ
NO_IMAGE_NO = {("leeseo", 27), ("leeseo", 70), ("leeseo", 122)}
TABLES = {"leeseo": ("イソ", LEESEO)}

if __name__ == "__main__":
    S = SP + "review/"
    seed = list(csv.reader(io.StringIO(open(PROJ + "public/seed/cards.csv", encoding="utf-8").read())))[1:]
    have = {(r[0], r[1], r[2], r[3]) for r in seed}
    # いまの画像がある枠
    imaged = set()
    for p in sorted(glob.glob(SP + "out/*.json")):
        if os.path.basename(p) == "zzzz_ida_check.json":
            continue
        for e in json.load(open(p, encoding="utf-8"))["images"]:
            if e["credit"] not in ("@powerofablink",):
                imaged.add((e["collection"], "/".join(e["members"]), e["source"], e["version"]))
    j = Job("zzzz_ida_check")
    report = []
    for key, (name, table) in TABLES.items():
        no = json.load(open(S + f"review_{key}.json"))
        miss = json.load(open(S + f"miss_{key}.json"))
        pages = {}
        for i in no:
            coll, src, ver, kind = table[i]
            page, b, _ = miss[i]
            if page not in pages:
                pages[page] = grid.load(D + f"{key}_{page}.jpg")
            im = pages[page]
            use_img = coll not in PAGE3 and src not in NO_IMAGE_SOURCES and (key, i) not in NO_IMAGE_NO
            img = im.crop(inset_frame(im, b)) if use_img else None
            if kind == X:
                report.append([name, i, coll, src, ver, "入れない"])
                continue
            if kind == H:
                if (coll, name, src, ver) not in have:
                    print("枠が見つからない", i, coll, src, ver)
                    report.append([name, i, coll, src, ver, "枠が見つからない"])
                    continue
                if img is not None and (coll, name, src, ver) not in imaged:
                    j.add(coll, [name], src, ver, img, "@idalshiro")
                    report.append([name, i, coll, src, ver, "画像を入れた"])
                else:
                    report.append([name, i, coll, src, ver, "枠あり（画像はそのまま）"])
                continue
            for m in MEMBERS:
                j.add(coll, [m], src, ver, img if m == name else None, "@idalshiro")
            report.append([name, i, coll, src, ver, "新しい枠（6 人）" + ("" if img is not None else "・画像なし")])
    j.save()
    with open(SP + "out/ida_check_report.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["member", "no", "collection", "source", "version", "result"])
        w.writerows(report)
    from collections import Counter
    print(Counter(r[-1] for r in report))
