"""画質を上げる（くり返し使う版、2026-09-30）：本人が追加した表のフォルダから、1 つのコレクションの画像を大きい方に差し替える

使い方：python hires_sheets.py "<pocamaster-images の中のフォルダ>" "<コレクション名>" "<出典>" <出力名>
  例：python hires_sheets.py "新しい資料 2026-09-30/LOVE DIVE_reina831wy" "LOVE DIVE" "@reina831wy" lovedive_0930

- 本人の指示：一覧版と種類ごとの表があるときは、種類ごとの表（カードが大きい）を使う → カードの横幅が MIN_CARD 未満の表は使わない
- カードの上に ID や透かしがある資料は、先に目で確かめて使わないこと（このスクリプトは透かしを見分けない）
- 同じ写真（似ている度合い TH 以上・2 番目と MARGIN 以上の差・3×4 のどのブロックも BLOCK_TH 以上）で、GAIN 倍以上大きいときだけ差し替える
- 自動で差し替えたものも必ず並べて目で見ること（ぼかしの画像に替わることがある。REVIVE+ で 2 枚あった → json から手で外した）
- 結果：out/zzz_hires_<出力名>.json（merge.py で後に読まれる）、確認用 out/hires_<出力名>_report.csv
"""
import csv, glob, json, os, sys
import numpy as np
from PIL import Image, ImageOps
import grid
from build2 import *
from hires_ida import feat, min_block

TH, MARGIN, GAIN, BLOCK_TH = 0.85, 0.05, 1.1, 0.55
MIN_CARD = int(os.environ.get("MIN_CARD", "190"))  # 小さい表しかないときは MIN_CARD=120 などで実行

if __name__ == "__main__":
    folder, coll, credit, name = sys.argv[1:5]
    out = "zzz_hires_" + name
    cur = {}
    for p in sorted(glob.glob(SP + "out/*.json")):
        if os.path.basename(p) == out + ".json":
            continue
        for e in json.load(open(p, encoding="utf-8"))["images"]:
            cur[(e["collection"], tuple(sorted(e["members"])), e["source"], e["version"])] = e
    cur = {k: e for k, e in cur.items() if len(e["members"]) == 1 and e["collection"] == coll and e["credit"] != "@powerofablink"}
    cands = []
    for f in sorted(glob.glob(ROOT + folder + "/*")):
        if not f.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
        for b in grid.card_boxes(im, min_w=0.04, max_w=0.35):
            if min(b[2] - b[0], b[3] - b[1]) < MIN_CARD:
                continue
            box = inset_frame(im, b); c = im.crop(box)
            cands.append((os.path.basename(f), box, c, feat(c)))
    F = np.array([c[3] for c in cands])
    j = Job(out); report = []
    for k, e in cur.items():
        old = Image.open(CARDS + e["file"]); s = F @ feat(old); o = np.argsort(-s)
        best, second = float(s[o[0]]), float(s[o[1]])
        fn, box, c, _ = cands[o[0]]
        ok = best >= TH and best - second >= MARGIN and min(c.size) >= min(old.size) * GAIN
        mb = min_block(old, c) if ok else 0.0
        ok = ok and mb >= BLOCK_TH
        report.append([e["members"][0], e["source"], e["version"], round(best, 3), round(second, 3), round(mb, 3), min(old.size), min(c.size), fn, "差し替え" if ok else ""])
        if ok:
            j.add(e["collection"], e["members"], e["source"], e["version"], c, credit)
    j.save()
    with open(SP + f"out/hires_{name}_report.csv", "w", encoding="utf-8-sig", newline="") as fo:
        w = csv.writer(fo); w.writerow(["member", "source", "version", "best", "second", "min_block", "old_w", "new_w", "sheet", "result"]); w.writerows(report)
    ws = sorted(r[6] for r in report); nw = sorted(min(c[2].size) for c in cands)
    print(f"表のカード {len(cands)}（横幅の中央値 {nw[len(nw)//2] if nw else '-'}px）、{coll} の画像 {len(cur)}（いまの横幅の中央値 {ws[len(ws)//2] if ws else '-'}px）、差し替え {sum(1 for r in report if r[-1])}")
