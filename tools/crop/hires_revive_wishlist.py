"""REVIVE+ の画質を上げる：6 人の wishlist（@idalshiro、カード 326×506px。新しい資料 2026-10-01/REVIVE+ 追加分/）から、
いまの画像と同じ写真を探して大きい画像に差し替える（枠はそのまま）。

- 表は 11 列 × 約 9 段（列 x=56+405c・段 y=1338+702r）。カードを囲む青い枠は 12px 内側に切って除く
- 似ている度合い TH 以上・2 番目との差 MARGIN 以上・3×4 のどのブロックも BLOCK_TH 以上・1.25 倍以上大きいときだけ差し替え
- ぼかし（未公開）のカードは使わない。結果：out/zzzzzz_revive_wishlist_hires.json、確認用 out/revive_wishlist_report.csv
- ユジンの表の「tjxxx」の ID（QQ MUSIC 2 の 5 枚目）の画像は使わない
"""
import csv, glob, json, os
import numpy as np
from PIL import Image
import grid
from build2 import *
from hires_ida import feat, min_block

D = ROOT + "新しい資料 2026-10-01/REVIVE+ 追加分/"
C = "REVIVE+"
EN = {"ユジン": "Yujin", "ガウル": "Gaeul", "レイ": "Rei", "ウォニョン": "Wonyoung", "リズ": "Liz", "イソ": "Leeseo"}
TH, MARGIN, GAIN, BLOCK_TH = 0.85, 0.05, 1.25, 0.35
SKIP = {"zzzzzz_revive_wishlist_hires.json"}
DROP_POS = {("ユジン", 3, 9)}  # tjxxx
BLUR_POS = {(7, 3), (7, 4), (7, 7), (7, 8), (7, 9)}  # ぼかし（未公開）：YETIMALL 1・2、NY MUSIC 2 LD（2 枚）、KMON 2。6 人とも同じ位置
box = lambda r, c: (56 + 405 * c + 12, 1338 + 702 * r + 12, 56 + 405 * c + 326 - 12, 1338 + 702 * r + 506 - 12)


def sharp(img):
    a = np.asarray(img.convert("L").resize((120, 180))).astype(float)
    return float(np.var(a[1:, :] - a[:-1, :]))


if __name__ == "__main__":
    cur = {}
    for p in sorted(glob.glob(SP + "out/*.json")):
        if os.path.basename(p) in SKIP:
            continue
        for e in json.load(open(p, encoding="utf-8"))["images"]:
            if e["collection"] == C and len(e["members"]) == 1 and e["credit"] != "@powerofablink":
                cur[(e["members"][0], e["source"], e["version"])] = e
    j = Job("zzzzzz_revive_wishlist_hires"); report = []
    for n, en in EN.items():
        im = grid.load(D + f"wishlist_{en}_idalshiro.jpg")
        cands = []
        for r in range(9):
            for c in range(11):
                if (n, r, c) in DROP_POS or (r, c) in BLUR_POS or 56 + 405 * c + 326 > im.width or 1338 + 702 * r + 506 > im.height:
                    continue
                cr = im.crop(box(r, c))
                if np.asarray(cr.convert("L")).std() < 12:  # 空き枠・「?」
                    continue
                cands.append((r, c, cr, feat(cr)))
        F = np.array([x[3] for x in cands])
        mine = [(k, e) for k, e in cur.items() if k[0] == n]
        nrep = 0
        for k, e in mine:
            old = Image.open(CARDS + e["file"]); s = F @ feat(old); o = np.argsort(-s)
            best, second = float(s[o[0]]), float(s[o[1]])
            r, c, cr, _ = cands[o[0]]
            mb = min_block(old, cr)
            ok = best >= TH and best - second >= MARGIN and mb >= BLOCK_TH and min(cr.size) >= min(old.size) * GAIN
            report.append([n, k[1], k[2], r, c, round(best, 3), round(second, 3), round(mb, 3), min(old.size), min(cr.size), "差し替え" if ok else ""])
            if ok:
                j.add(C, [n], k[1], k[2], cr, "@idalshiro"); nrep += 1
        print(n.encode("ascii", "replace").decode(), "差し替え", nrep, "/", len(mine))
    j.save()
    with open(SP + "out/revive_wishlist_report.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f); w.writerow(["member", "source", "version", "row", "col", "best", "second", "min_block", "old_w", "new_w", "result"]); w.writerows(report)
