"""ほかの 5 人のノンアルバムの見比べ（_review/<メンバー>_na_have.html、2026-10-01）の結果を反映する（albums_ida_na_have.py と同じ）

- 「ちがう」は 5 人とも 50（FC の電話タブ特典）だけ（リズはなし）→ 表の画像に入れ替え
- 「同じ」は、表の画像が 1.1 倍以上大きいときだけ入れ替える
"""
import csv, glob, json, os
import grid
from build2 import *
from review_na_have import ITEMS, D, KEYS, nearest

DIFF = {"ユジン": {50}, "ガウル": {50}, "レイ": {50}, "ウォニョン": {50}, "リズ": set()}
CREDIT = "@idalshiro"

if __name__ == "__main__":
    miss = json.load(open(SP + "review/miss_na_leeseo.json", encoding="utf-8"))
    allrows = list(csv.DictReader(open(PROJ + "public/seed/cards.csv", encoding="utf-8")))
    cur = {}
    for p in sorted(glob.glob(SP + "out/*.json")):
        if os.path.basename(p) == "zzzzz_na_have_others.json":
            continue
        for e in json.load(open(p, encoding="utf-8"))["images"]:
            if len(e["members"]) == 1:
                cur[(e["members"][0], e["collection"], e["source"], e["version"])] = e
    j = Job("zzzzz_na_have_others")
    for key, name in KEYS:
        if name == "イソ":
            continue
        im = grid.load(D + f"{key}_na.jpg")
        bs = grid.card_boxes(im, min_w=0.03, max_w=0.08)
        rows = [r for r in allrows if r["member"] == name]
        n = 0
        for idx, (csub, ssub, ver, lab) in ITEMS.items():
            f = [r for r in rows if csub in r["collection"] and r["source"].startswith(ssub) and r["version"] == ver]
            if len(f) != 1:
                continue
            r = f[0]; e = cur.get((name, r["collection"], r["source"], r["version"]))
            if e is None:
                continue
            x0, y0, x1, y1 = miss[idx][1]
            b = nearest(bs, (x0 + x1) / 2, (y0 + y1) / 2)
            if b is None:
                continue
            new = im.crop(inset_frame(im, b)); ow = min(Image.open(CARDS + e["file"]).size)
            if idx in DIFF[name] or min(new.size) >= ow * 1.1:
                j.add(r["collection"], [name], r["source"], r["version"], new, CREDIT); n += 1
        print(name, n)
    j.save()
