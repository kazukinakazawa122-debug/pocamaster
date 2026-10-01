"""イソのノンアルバムの見比べ（_review/leeseo_na_have.html、2026-10-01）の結果を反映する

- 「ちがう」＝表の画像のほうが正しい → 枠の画像を表の画像に入れ替える：50（FC の電話タブ特典）
- 「同じ」＝大きいほうを使う → 表の画像が 1.1 倍以上大きいときだけ入れ替える（ほぼ同じ大きさなら、いまの画像のまま）
"""
import csv, glob, json, os
import grid
from build2 import *
from review_na_have import ITEMS, D

DIFF = {50}
CREDIT = "@idalshiro"
SKIP = {"zzzzz_na_have_leeseo.json"}

if __name__ == "__main__":
    miss = json.load(open(SP + "review/miss_na_leeseo.json", encoding="utf-8"))
    rows = [r for r in csv.DictReader(open(PROJ + "public/seed/cards.csv", encoding="utf-8")) if r["member"] == "イソ"]
    cur = {}
    for p in sorted(glob.glob(SP + "out/*.json")):
        if os.path.basename(p) in SKIP:
            continue
        for e in json.load(open(p, encoding="utf-8"))["images"]:
            if e["members"] == ["イソ"]:
                cur[(e["collection"], e["source"], e["version"])] = e
    im = grid.load(D + "leeseo_na.jpg")
    j = Job("zzzzz_na_have_leeseo")
    for idx, (csub, ssub, ver, lab) in ITEMS.items():
        f = [r for r in rows if csub in r["collection"] and r["source"].startswith(ssub) and r["version"] == ver]
        r = f[0]; e = cur[(r["collection"], r["source"], r["version"])]
        new = im.crop(inset_frame(im, miss[idx][1])); ow = min(Image.open(CARDS + e["file"]).size)
        use = idx in DIFF or min(new.size) >= ow * 1.1
        print(idx, r["source"][:20].encode("ascii", "replace").decode(), r["version"].encode("ascii", "replace").decode(), ow, min(new.size), "入れ替え" if use else "")
        if use:
            j.add(r["collection"], ["イソ"], r["source"], r["version"], new, CREDIT)
    j.save()
