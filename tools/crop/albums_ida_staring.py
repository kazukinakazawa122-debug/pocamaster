"""SuperStar POP-UP 'STAR+ING: Christmas Bear' の Best・Winter（@idalshiro のノンアルバムのページ、2026-10-01）

- 表の 203 番＝Christmas（すでに入れた）、204 番＝Best（カードに「Blue Heart#2」）、205 番＝Winter。
  リズの枠にすでにある画像と同じ写真で確かめた（203＝Christmas・205＝Winter。204 は残りの Best）
- 6 人とも同じ位置。枠にまだ画像のないメンバーにだけ入れる。STAR+ING Tokyo は @idalshiro の表にない
"""
import csv, glob, json, os
import grid
from build2 import *
from review_na_have import KEYS, nearest, D

SRC = {204: "Best", 205: "Winter"}
if __name__ == "__main__":
    miss = json.load(open(SP + "review/miss_na_leeseo.json", encoding="utf-8"))
    allrows = list(csv.DictReader(open(PROJ + "public/seed/cards.csv", encoding="utf-8")))
    have = set()
    for p in sorted(glob.glob(SP + "out/*.json")):
        if os.path.basename(p) == "idalshiro_staring.json":
            continue
        for e in json.load(open(p, encoding="utf-8"))["images"]:
            have.add((e["collection"], tuple(e["members"]), e["source"], e["version"]))
    j = Job("idalshiro_staring")
    for key, name in KEYS:
        im = grid.load(D + f"{key}_na.jpg")
        bs = grid.card_boxes(im, min_w=0.03, max_w=0.08)
        for idx, ver in SRC.items():
            f = [r for r in allrows if r["member"] == name and r["source"].startswith("SuperStar POP-UP") and r["version"] == ver]
            if len(f) != 1 or (f[0]["collection"], (name,), f[0]["source"], ver) in have:
                continue
            x0, y0, x1, y1 = miss[idx][1]
            b = nearest(bs, (x0 + x1) / 2, (y0 + y1) / 2)
            if b is None:
                print("見つからない", name, idx); continue
            j.add(f[0]["collection"], [name], f[0]["source"], ver, im.crop(inset_frame(im, b)), "@idalshiro")
    j.save()
