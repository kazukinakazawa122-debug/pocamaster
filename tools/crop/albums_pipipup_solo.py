"""@_pipipup の「SOLO Contracts」（ユジンの広告・イベントのトレカ。pocamaster-images/新しい資料 2026-10-01/…/SOLO Contracts_ユジン.png）

- 段：Dewi Tree 4・CLIO 12＋12・HANA BANK 11・NEPA 12・Dongwon Tuna 4・Maxim 2
- アプリのユジン個人（@idalshiro の solo merch から入れた 63 枚）と写真を突き合わせた（2026-10-01、目でも確認）：
  CLIO の 1 段目 12 枚・HANA BANK の最初の 3 枚・Dewi Tree・NEPA・Dongwon Tuna・Maxim はすでにある（大きさもほぼ同じ）
- 新しいもの：CLIO の 2 段目 12 枚（CLIO Japan・Every Fruit Grocery・#Luxury Koshort Edition。それぞれ A Ver 2 枚＋B Ver 2 枚）、
  HANA BANK の残り 8 枚（TRAVLOG Good Lack (Amulet) PC 4・DaldalHana Seongsu Daldal Factory 2・DaldalHana 2）
- 命名はアプリの CLIO（「1（2023.1）-1」）に合わせた
"""
import json, os
import grid
from build2 import *
from albums_pipipup import D, CREDIT

YUJIN = "Yujin Solo｜ユジン個人"
NEWS = [  # (段, 先頭の番号, 入手元, [バージョン...])
    (2, 0, "CLIO", ["4（CLIO Japan）-1", "4（CLIO Japan）-2", "4（CLIO Japan）-3", "4（CLIO Japan）-4",
                     "5（Every Fruit Grocery）-1", "5（Every Fruit Grocery）-2", "5（Every Fruit Grocery）-3", "5（Every Fruit Grocery）-4",
                     "6（#Luxury Koshort Edition）-1", "6（#Luxury Koshort Edition）-2", "6（#Luxury Koshort Edition）-3", "6（#Luxury Koshort Edition）-4"]),
    (3, 3, "Hana Bank", ["TRAVLOG Good Lack（Amulet）PC-1", "TRAVLOG Good Lack（Amulet）PC-2", "TRAVLOG Good Lack（Amulet）PC-3", "TRAVLOG Good Lack（Amulet）PC-4",
                          "DaldalHana Seongsu Daldal Factory-1", "DaldalHana Seongsu Daldal Factory-2", "DaldalHana-1", "DaldalHana-2"]),
]
DROP = set()  # 目で見て ID の透かしがあった (段, 番号)
if os.path.exists(SP + "pp_solo_drop.json"):
    DROP = {tuple(x) for x in json.load(open(SP + "pp_solo_drop.json"))}


def rows_of(im):
    bs = sorted(grid.card_boxes(im, min_w=0.025, max_w=0.09), key=lambda b: (b[1] + b[3]) / 2)
    rows = []
    for b in bs:
        cy = (b[1] + b[3]) / 2
        if rows and abs(cy - rows[-1][0]) < 120:
            rows[-1][1].append(b)
        else:
            rows.append([cy, [b]])
    return [sorted(r[1], key=lambda b: b[0]) for r in rows]


def fixed_boxes(row):
    """検出した箱は色のうすいカードで欠けることがあるので、段ごとに大きさ・間隔をそろえた箱にする（1 枚目はタブや白でずれるので使わない）"""
    xs = np.array([b[0] for b in row[1:]]); idx = np.arange(1, len(row))
    ws = np.array([b[2] - b[0] for b in row[1:]]); hs = np.array([b[3] - b[1] for b in row[1:]])
    w, h = float(np.median(ws)), float(np.median(hs))
    pitch = float(np.median(np.diff(xs))); a = float(np.median(xs - pitch * idx))
    y0 = float(np.median([b[1] for b in row]))
    return [(a + pitch * i, y0, a + pitch * i + w, y0 + h) for i in range(len(row))]


if __name__ == "__main__":
    im = grid.load(D + "SOLO Contracts_ユジン.png")
    rows = [fixed_boxes(r) for r in rows_of(im)]
    j = Job("pipipup_solo")
    for r, c0, src, vers in NEWS:
        for k, v in enumerate(vers):
            c = c0 + k
            if (r, c) in DROP:
                print("透かしで外す", r, c); j.add(YUJIN, ["ユジン"], src, v, None, CREDIT); continue
            j.add(YUJIN, ["ユジン"], src, v, im.crop(tuple(int(v) for v in (rows[r][c][0] + 5, rows[r][c][1] + 5, rows[r][c][2] - 5, rows[r][c][3] - 5))), CREDIT)
    j.save()
