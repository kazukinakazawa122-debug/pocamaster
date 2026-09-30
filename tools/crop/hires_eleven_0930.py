"""画質を上げる：本人が 2026-09-30 に追加した ELEVEN の種類ごとの表（@reina831wy、pocamaster-images/新しい資料 2026-09-30/ELEVEN_reina831wy/）

- 本人の指示どおり、メンバー別の一覧・まとめの表（ファイル名の並びで先頭 8 枚）は使わず、種類ごとの表だけ使う
- カードの上に透かしはない（表の右下に作者名があるだけ）
- いまの ELEVEN の画像（1 人のカード）と同じ写真（hires_0930.py と同じ基準）で、GAIN 倍以上大きいときだけ差し替える
- 結果：out/zzz_hires_eleven_0930.json、確認用 out/hires_eleven_0930_report.csv
"""
import csv, glob, json, os
import numpy as np
from PIL import Image, ImageOps
import grid
from build2 import *
from hires_ida import feat, min_block

D = ROOT + "新しい資料 2026-09-30/ELEVEN_reina831wy/"
TH, MARGIN, GAIN, BLOCK_TH = 0.85, 0.05, 1.1, 0.55
MIN_CARD = 190  # これより小さいカードの表（まとめの表など）は使わない
OUT = "zzz_hires_eleven_0930"

if __name__ == "__main__":
    cur = {}
    for p in sorted(glob.glob(SP + "out/*.json")):
        if os.path.basename(p) == OUT + ".json":
            continue
        for e in json.load(open(p, encoding="utf-8"))["images"]:
            cur[(e["collection"], tuple(sorted(e["members"])), e["source"], e["version"])] = e
    cur = {k: e for k, e in cur.items() if len(e["members"]) == 1 and e["collection"] == "ELEVEN" and e["credit"] != "@powerofablink"}
    cands = []
    for f in sorted(glob.glob(D + "*.jpg"))[8:]:
        im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
        for b in grid.card_boxes(im, min_w=0.04, max_w=0.35):
            if min(b[2] - b[0], b[3] - b[1]) < MIN_CARD:
                continue
            box = inset_frame(im, b); c = im.crop(box)
            cands.append((os.path.basename(f), box, c, feat(c)))
    F = np.array([c[3] for c in cands])
    j = Job(OUT); report = []
    for k, e in cur.items():
        old = Image.open(CARDS + e["file"]); s = F @ feat(old); o = np.argsort(-s)
        best, second = float(s[o[0]]), float(s[o[1]])
        fn, box, c, _ = cands[o[0]]
        ok = best >= TH and best - second >= MARGIN and min(c.size) >= min(old.size) * GAIN
        mb = min_block(old, c) if ok else 0.0
        ok = ok and mb >= BLOCK_TH
        report.append([e["members"][0], e["source"], e["version"], round(best, 3), round(second, 3), round(mb, 3), min(old.size), min(c.size), fn, "差し替え" if ok else ""])
        if ok:
            j.add(e["collection"], e["members"], e["source"], e["version"], c, "@reina831wy")
    j.save()
    with open(SP + f"out/{OUT[4:]}_report.csv", "w", encoding="utf-8-sig", newline="") as fo:
        w = csv.writer(fo); w.writerow(["member", "source", "version", "best", "second", "min_block", "old_w", "new_w", "sheet", "result"]); w.writerows(report)
    print("表のカード", len(cands), "ELEVEN の画像", len(cur), "差し替え", sum(1 for r in report if r[-1]))
