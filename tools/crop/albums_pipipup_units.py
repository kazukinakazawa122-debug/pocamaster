"""@_pipipup の MD List 02 の「ランダムパック」の 2 人のカード（ユニット）

- 各メンバーの表の 6〜10 番目（MAGAZINE IVE は 5 段目、SHOW WHAT I HAVE は 4 段目）が、自分と「ほかの 5 人」の 2 人のカード。
  相手は顔ではなく、ほかの表で同じ写真を探して決める（似ている度合い 0.7 以上でお互いに一番似ているもの）。
  並びはほとんど「ユジン・ガウル・レイ・ウォニョン・リズ・イソ」の順だが、イソの MAGAZINE IVE の表だけリズとウォニョンが逆だった
- 同じカードが 2 人の表に載っているので、大きいほうを使う
- MAGAZINE IVE：ユニットの枠は 15 組なかったので足す（入手元「Random Photocard Pack」・バージョン「ユニット」）
- SHOW WHAT I HAVE：枠は 15 組ある（Random Photocard / ユニット）。画像のない枠、またはこちらが 1.25 倍以上大きい枠に入れる
"""
import csv, glob, json, os
from albums_pipipup import table, NAMES, align, CREDIT, MAG, SWIH
from build2 import *
from hires_ida import feat

SETS = [(MAG, 5, "Random Photocard Pack"), (SWIH, 4, "Random Photocard")]
if __name__ == "__main__":
    tabs = {n: table(n) for n in NAMES}
    al = align(tabs)
    cur = {}
    for p in sorted(glob.glob(SP + "out/*.json")):
        if os.path.basename(p) == "pipipup_units.json":
            continue
        for e in json.load(open(p, encoding="utf-8"))["images"]:
            cur[(e["collection"], tuple(e["members"]), e["source"], e["version"])] = e
    j = Job("pipipup_units")
    for coll, r, src in SETS:
        cards = {}
        for n in NAMES:
            for c in range(5, 10):
                if (n, r, c) in al:
                    im, b = al[(n, r, c)]
                    crop = im.crop(inset_frame(im, b))
                    cards[(n, c)] = (crop, feat(crop))
        partner = {}
        for (n, c), (crop, f) in cards.items():
            s_, m, d = max(((float(f @ g), m, d) for (m, d), (_, g) in cards.items() if m != n), key=lambda t: t[0])
            if s_ >= 0.7:
                partner[(n, c)] = (m, d)
        best = {}
        for (n, c), (m, d) in partner.items():
            if partner.get((m, d)) != (n, c):
                continue  # お互いに一番似ていないものは使わない
            pair = tuple(sorted((n, m), key=NAMES.index))
            crop = cards[(n, c)][0]
            if pair not in best or min(crop.size) > min(best[pair].size):
                best[pair] = crop
        for pair in sorted(best, key=lambda p: (NAMES.index(p[0]), NAMES.index(p[1]))):
            old = cur.get((coll, pair, src, "ユニット"))
            if old is not None and min(best[pair].size) < min(Image.open(CARDS + old["file"]).size) * 1.25:
                continue
            j.add(coll, list(pair), src, "ユニット", best[pair], CREDIT)
        print(coll[:14], len(best), "組")
    j.save()
