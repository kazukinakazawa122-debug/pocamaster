"""@idalshiro の「solo merch template」（メンバー 1 人ずつの個人の広告・イベントのトレカ）

- 資料：pocamaster-images/_nonalbum/idalshiro/solo/<メンバー>.jpg（4500×8000、ウォニョンは 2 枚）
  drive：tinyurl.com/idalshiro → IVE → solo merch
- ラベルは目で読んだ（2026-09-30）。カードは上の段から、段の中は左から数える
- 入れ先：メンバーごとの「個人（ソロ）」のコレクション（本人の要望）。ユジン・ガウル・レイ・イソは新しく作る
- 入れないもの：
  - ウォニョンの Kirsh・SKT・Pepsi・Hapa Kristin 1〜4・innisfree・GOSPHERES・AMUSE 1〜2・EIDER 1（アプリのウォニョン個人・Pepsi にある）
  - イソの Pepsi（2022、Pepsi のコレクションにある）
  - リズ（powercircles・WAVES・8seconds・s.nature、@balsegno の資料から入れたものと同じ）
"""
import grid
from build2 import *

D = ROOT + "_nonalbum/idalshiro/solo/"
CREDIT = "@idalshiro"


def n(prefix, k):
    """"1-1"〜"1-k" のような番号"""
    return [f"{prefix}{i}" for i in range(1, k + 1)]


def boxes(key, inserts=()):
    """カードの位置を上の段から並べる。見つからなかったカードは、同じ段の隣どうしの真ん中に足す"""
    im = grid.load(D + key + ".jpg")
    bs = sorted((b for b in grid.card_boxes(im, min_w=0.05, max_w=0.2) if b[1] > 500), key=lambda b: (b[1] + b[3]) / 2)
    rows = []
    for b in bs:
        cy = (b[1] + b[3]) / 2
        if rows and abs(cy - rows[-1][0]) < 120:
            rows[-1][1].append(b)
        else:
            rows.append([cy, [b]])
    rows = [sorted(r, key=lambda b: b[0]) for _, r in rows]
    for r, c in inserts:  # r 段目の c 番目（0 から）に足す
        a, b = rows[r][c - 1], rows[r][c]
        w = a[2] - a[0]
        x0 = (a[2] + b[0]) / 2 - w / 2
        rows[r].insert(c, (x0, a[1], x0 + w, a[3]))
    return im, [b for r in rows for b in r]


# (コレクション, 資料, 足す位置, [(開始番号, 入手元, [バージョン...]), ...])  開始番号は上から通しで数えた番号
YUJIN = "Yujin Solo｜ユジン個人"
GAEUL = "Gaeul Solo｜ガウル個人"
REI = "Rei Solo｜レイ個人"
WY = "Wonyoung Solo｜ウォニョン個人"
LEESEO = "Leeseo Solo｜イソ個人"
SHEETS = [
    (YUJIN, "yujin", [(5, 5)], [
        (0, "dewy tree", n("", 4)), (4, "NEPA", n("1-", 4)), (8, "Hana Bank", ["1"]), (9, "Hana Bank", ["2023.6-1", "2023.6-2"]),
        (11, "CLIO", n("1（2023.1）-", 4)), (15, "CLIO", n("2（2023.3）-", 3)), (18, "CLIO", n("3（2023.9）-", 4)), (22, "NEPA", n("2-", 4)),
        (26, "Dongwon Tuna", ["1-1", "1-2"]), (28, "Maxim Coffee", n("1-", 2)), (30, "Dongwon Tuna", n("2-", 2)), (32, "NEPA", n("3-", 4)),
        (36, "LABO-H", n("1-", 4)), (40, "arena HOMME+", ["A 1", "A 2", "B 1", "B 2", "C 1", "C 2"]),
        (46, "L'OFFICIEL HOMMES", n("A ", 4) + n("B ", 4) + n("C ", 2)),
        (56, "Maxim Coffee", n("2-", 2) + n("3-", 2)), (60, "LABO-H", n("2-", 3)),
    ]),
    (GAEUL, "gaeul", [], [
        (0, "tadapops", n("A ", 3) + n("B ", 3) + n("C（bundle）", 2)), (8, "Focus Star", n("", 6)),
    ]),
    (REI, "rei", [], [
        (0, "BONAJOUR", n("", 3)), (3, "FCMM", n("1-", 4) + n("2-", 3)),
        (10, "peach C", n("1-", 4) + n("2-", 4) + n("3 Global ", 4) + n("3 Japan ", 4) + n("4 Global ", 4) + n("4 Japan ", 2)),
        (32, "Opening Project", n("1-", 5) + n("2-", 5) + n("3-", 4) + n("4-", 4)),
        (50, "LUNA", n("1-", 4)), (54, "fully", n("レンチキュラー ", 2)),
        (56, "Knight", ["A 1", "A 2", "B 1", "B 2", "C 1", "C 2"] + n("ランダム ", 5)),
        (67, "rom'u", n("Set ", 3) + [""]), (71, "millet", n("Set ", 4)), (75, "LUNA", n("2-", 4)),
        (79, "MISEKI", ["", "Seoul Set 1", "Seoul Set 2"]),
    ]),
    (LEESEO, "leeseo", [], [
        (6, "THE NORTH FACE", n("2023.11-", 4)),
        (10, "the SAEM", n("18 KRW Set ", 4) + n("Highlighter Set ", 2) + n("Toning Cushion Set ", 2)),
        (18, "DELING magazine", n("", 6) + n("POLA ", 6)),
    ]),
    (WY, "wonyoung", [], [
        (47, "Hapa Kristin", n("5-", 4)), (65, "Hapa Kristin", n("6-", 4)), (69, "AMUSE", n("3-", 4)), (73, "rolarola", n("1-", 4)),
        (77, "EIDER", n("2-", 4)), (81, "Hapa Kristin", n("7-", 4)), (85, "AMUSE", n("4-", 3)), (88, "rolarola", n("2-", 2)),
        (90, "AMUSE × Hello Kitty", [""]), (91, "rolarola", n("3-", 2)), (93, "Hapa Kristin", n("8-", 4)), (97, "AMUSE", n("6-", 3)),
        (100, "EIDER", n("3-", 4)), (104, "GRAZIA magazine", n("", 3)), (107, "sense magazine", n("", 3) + n("POLA ", 4)),
        (114, "Hapa Kristin", n("9-", 4)), (118, "AMUSE", n("7-", 3)), (121, "rolarola", n("4-", 4) + n("5-", 4)),
        (129, "malto", n("", 2)), (131, "Woori Bank", n("1-", 4)), (135, "Binggrae", n("", 4)), (139, "Dashing Diva", n("1-", 2)),
        (141, "AMUSE", ["8"]), (142, "AMUSE", n("9-", 3)), (145, "Dashing Diva", n("2-", 2)),
        (147, "super ELLE magazine", n("", 4) + n("POLA ", 5)),
    ]),
    (WY, "wonyoung_2", [(2, 7)], [
        (0, "medicube", n("", 4)), (4, "EIDER", n("4-", 4)), (8, "rolarola", n("6-", 4)), (12, "Dashing Diva", ["3"]),
        (13, "rolarola", n("7-", 4)), (17, "Woori Bank", n("2-", 4)),
        (21, "D'ICON 'one & only'", n("Type A ", 3) + n("Type B ", 3) + n("Type C ", 3) + n("Type D ", 3)),
        (33, "Kakao 予約特典", n("", 4)), (37, "D-MALL 予約特典", n("", 4)), (41, "Hapa Kristin", n("10-", 4)),
    ]),
]
MEMBER = {YUJIN: "ユジン", GAEUL: "ガウル", REI: "レイ", WY: "ウォニョン", LEESEO: "イソ"}

if __name__ == "__main__":
    j = Job("solo_idalshiro")
    for coll, key, inserts, groups in SHEETS:
        im, bs = boxes(key, inserts)
        for start, src, vers in groups:
            for k, v in enumerate(vers):
                j.add(coll, [MEMBER[coll]], src, v, im.crop(tuple(int(x) for x in bs[start + k])), CREDIT)
    j.save()
