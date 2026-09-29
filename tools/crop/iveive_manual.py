"""I've IVE：自動で合わなかった枠を、目で確かめて @youngningz の HD 版のカードに割り当てる（2026-09-29）
（rest の順番と、表のカードの番号は、確認用シートで見たものと同じになる）"""
import json, glob, csv, os
from PIL import Image
from build2 import *
Image.MAX_IMAGE_PIXELS = None
D = ROOT + "I've IVE/youngningz_HD/"
MEM = {"yujin": "ユジン", "gaeul": "ガウル", "rei": "レイ", "wonyoung": "ウォニョン", "liz": "リズ", "leeseo": "イソ"}
last = {}
for p in sorted(glob.glob(SP + "out/*.json")):
    if "zz_ri_I_ve" in p or "iveive_manual" in p:
        continue
    for e in json.load(open(p, encoding="utf-8"))["images"]:
        if e["collection"] == "I've IVE":
            last[("/".join(e["members"]), e["source"], e["version"])] = e
got = {(x["members"], x["source"], x["version"]) for x in csv.DictReader(open(SP + "out/ri_report_I_ve_IVE_youngningz_HD.csv", encoding="utf-8-sig")) if x["result"]}
rest = [e for k, e in last.items() if e["credit"] == "@powerofablink" and k not in got]
cands = {}
for f in os.listdir(D):
    m = MEM[f.split(". ")[1].split(".")[0]]
    im = grid.load(D + f)
    bs = grid.card_boxes(im, ratio=(1.2, 1.8), min_w=0.05, max_w=0.2) + grid.card_boxes(im, ratio=(0.6, 1.19), min_w=0.07, max_w=0.25)
    cands[m] = [im.crop(tuple(int(v) for v in b)) for b in bs]
PICK = {0: 13, 1: 27, 2: 28, 5: 0, 6: 4, 7: 28, 8: 29, 9: 15, 10: 22, 11: 28, 12: 29, 14: 28, 16: 28, 20: 6, 22: 30, 23: 25}
j = Job("zz_ri_iveive_manual")
for r, k in PICK.items():
    e = rest[r]
    j.add(e["collection"], e["members"], e["source"], e["version"], cands[e["members"][0]][k], "@youngningz")
j.save()
for r, e in enumerate(rest):
    if r not in PICK:
        print("画像なしのまま", *e["members"], e["source"], e["version"])
