"""画質を上げる：本人が 2026-09-30 に追加した 1 種類ずつの表（pocamaster-images/新しい資料 2026-09-30/）から切り出し直す

- 本人の指示：一覧版と 1 種類ずつの画像がどちらもあるときは、画質のよい 1 種類ずつの方を使う → 一覧版（メンバー別一覧・MD まとめ・小さい方）は使わない
- いまの画像（1 人のカード）と同じ写真（似ている度合い TH 以上・2 番目と MARGIN 以上の差・3×4 のどのブロックも BLOCK_TH 以上）で、
  GAIN 倍以上大きいときだけ差し替える。枠はいまのまま
- 結果：out/zzz_hires_0930.json（merge.py でいちばん後に読まれる）、確認用 out/hires_0930_report.csv
"""
import csv, glob, json, os
import numpy as np
from PIL import Image, ImageOps
import grid
from build2 import *
from hires_ida import feat, min_block

D = ROOT + "新しい資料 2026-09-30/"
SKIP_WORDS = ("メンバー別一覧", "MD まとめ", "小さい方", "ALIVE_全員一覧")
TH, MARGIN, GAIN, BLOCK_TH = 0.85, 0.05, 1.25, 0.55
# 目で見て同じ写真だと確かめたもの（2026-09-30）：IVE SCOUT の Random Photocard Pack 1〜4 の 24 枚は、切り方と色がちがうため
# ブロックごとの一致が低く出るが、並べて見るとどれも同じ写真 → いちばん似ているカードで差し替える
CONFIRMED = {("3rd FAN CONCERT 'IVE SCOUT'", "Random Photocard Pack")}
COLLS = {"1st WORLD TOUR 'SHOW WHAT I HAVE'", "3rd FAN CONCERT 'IVE SCOUT'", "DIVE Official Fanclub｜ファンクラブ",
         "Collab & Event｜コラボ・イベント", "2nd WORLD TOUR 'SHOW WHAT I AM'", "2nd FANMEETING 'MAGAZINE IVE'", "1st FAN CONCERT 'The Prom Queens'"}


def credit_of(fn):
    return "@ri__chan94" if "ri__chan94" in fn else "@reina831wy" if "reina831wy" in fn else ""


if __name__ == "__main__":
    cur = {}
    for p in sorted(glob.glob(SP + "out/*.json")):
        if os.path.basename(p) in ("zzz_hires_0930.json", "zzz_0930.json"):  # 今回の表から作ったものは対象にしない
            continue
        for e in json.load(open(p, encoding="utf-8"))["images"]:
            cur[(e["collection"], tuple(sorted(e["members"])), e["source"], e["version"])] = e
    cur = {k: e for k, e in cur.items() if len(e["members"]) == 1 and e["collection"] in COLLS and e["credit"] != "@powerofablink"}
    cands = []
    for f in sorted(glob.glob(D + "*.jpg")):
        fn = os.path.basename(f)
        if any(w in fn for w in SKIP_WORDS) or not credit_of(fn):
            continue
        im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
        for b in grid.card_boxes(im, min_w=0.04, max_w=0.35):
            box = inset_frame(im, b); c = im.crop(box)
            cands.append((fn, box, c, feat(c)))
    F = np.array([c[3] for c in cands])
    j = Job("zzz_hires_0930"); report = []
    for k, e in cur.items():
        old = Image.open(CARDS + e["file"]); s = F @ feat(old); o = np.argsort(-s)
        best, second = float(s[o[0]]), float(s[o[1]])
        fn, box, c, _ = cands[o[0]]
        ok = best >= TH and best - second >= MARGIN and min(c.size) >= min(old.size) * GAIN
        mb = min_block(old, c) if ok else 0.0
        ok = ok and mb >= BLOCK_TH
        if (e["collection"], e["source"]) in CONFIRMED and "IVE SCOUT_Random" in fn:
            ok = best >= 0.6 and min(c.size) >= min(old.size) * GAIN
        if best >= 0.7:
            report.append([e["collection"], e["members"][0], e["source"], e["version"], round(best, 3), round(second, 3), round(mb, 3), min(old.size), min(c.size), fn, "差し替え" if ok else ""])
        if ok:
            j.add(e["collection"], e["members"], e["source"], e["version"], c, credit_of(fn))
    j.save()
    with open(SP + "out/hires_0930_report.csv", "w", encoding="utf-8-sig", newline="") as fo:
        w = csv.writer(fo); w.writerow(["collection", "member", "source", "version", "best", "second", "min_block", "old_w", "new_w", "sheet", "result"]); w.writerows(report)
    print("表のカード", len(cands), "差し替え", sum(1 for r in report if r[-1]))
