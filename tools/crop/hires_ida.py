"""画質を上げる：@idalshiro のメンバー別の全トレカ一覧（_nonalbum/idalshiro/<メンバー>_1〜3・_na.jpg）から、
いまの画像と同じ写真を探し、大きい方に差し替える（枠はそのまま）。

- そのメンバー 1 人のカードだけ（ユニット・全員のカードは表に同じ写真がないことが多いので対象外）
- 似ている度合い TH 以上で、2 番目に似ているものより MARGIN 以上似ているときだけ同じ写真とみなす
- いまの画像より GAIN 倍以上大きくなるときだけ差し替える
- 表のカードを囲むメンバーの色の枠は inset_frame で除く（本人の指摘：ピンクの背景が入っている）
- 結果：out/zzz_ida_hires.json（merge.py でいちばん後に読まれ、同じカードの画像を置き換える）、確認用 out/ida_hires_report.csv
"""
import csv, glob, json, os
import numpy as np
from PIL import Image
import grid
from build2 import *

D = ROOT + "_nonalbum/idalshiro/"
KEYS = [("yujin", "ユジン"), ("gaeul", "ガウル"), ("rei", "レイ"), ("wonyoung", "ウォニョン"), ("liz", "リズ"), ("leeseo", "イソ")]
TH, MARGIN, GAIN = 0.85, 0.05, 1.25
BLOCK_TH = 0.55  # 3×4 のブロックごとの似ている度合いの最低（上に重ねた文字・スタンプや、別の写真を外す）
SKIP = {"idalshiro.json", "solo_idalshiro.json", "zzz_ida_hires.json"}
# 目で見て外したもの：お店の透かし（BOYCOTT）が写っている表の画像（2026-09-30）
DROP = set()  # 本人：BOYCOTT の印は使ってよい（2026-09-30）。前は ida_drop.json の 2 枚を外していた


def trim_pink(c):
    """端にピンクの枠が残っていたら、なくなるまで少しずつ内側を切る（最大 3 回）"""
    for _ in range(3):
        a = np.asarray(c.convert("RGB")).astype(int)
        edge = np.concatenate([a[:3].reshape(-1, 3), a[-3:].reshape(-1, 3), a[:, :3].reshape(-1, 3), a[:, -3:].reshape(-1, 3)])
        pink = ((edge[:, 0] > 200) & (edge[:, 0] - edge[:, 1] > 35) & (edge[:, 2] - edge[:, 1] > 5)).mean()
        if pink < 0.1:
            break
        w, h = c.size
        c = c.crop((int(w * .02), int(h * .02), w - int(w * .02), h - int(h * .02)))
    return c


def feat(img):
    """中央 80% を 24×36 に縮め、明るさ・色の差をならした特徴（hires.py と同じ）"""
    w, h = img.size
    if w > h:
        img = img.rotate(90, expand=True)
        w, h = img.size
    a = np.asarray(img.crop((w * .1, h * .1, w * .9, h * .9)).convert("RGB").resize((24, 36), Image.BILINEAR)).astype(float)
    a = a - a.mean(axis=(0, 1))
    a = a / (a.std() + 1e-6)
    return a.flatten() / np.sqrt(a.size)


def blocks(img):
    """白黒 36×48 にして 3×4 のブロックに分け、ブロックごとに明るさをならしたもの"""
    w, h = img.size
    a = np.asarray(img.crop((w * .04, h * .04, w * .96, h * .96)).convert("L").resize((36, 48), Image.BILINEAR)).astype(float)
    out = []
    for by in range(4):
        for bx in range(3):
            b = a[by * 12:(by + 1) * 12, bx * 12:(bx + 1) * 12]
            b = b - b.mean()
            out.append(b.flatten() / (np.linalg.norm(b) + 1e-6))
    return out


def min_block(a, b):
    return min(float(x @ y) for x, y in zip(blocks(a), blocks(b)))


if __name__ == "__main__":
    # いま使っている画像（merge.py と同じく、あとの json が前のものを上書きする）
    cur = {}
    for p in sorted(glob.glob(SP + "out/*.json")):
        if os.path.basename(p) in SKIP:
            continue
        for e in json.load(open(p, encoding="utf-8"))["images"]:
            cur[(e["collection"], tuple(sorted(e["members"])), e["source"], e["version"])] = e
    cur = {k: e for k, e in cur.items() if len(e["members"]) == 1 and e["credit"] != "@powerofablink" and not e["source"].startswith("グッズ｜")}

    j = Job("zzz_ida_hires")
    report = []
    for key, name in KEYS:
        # 表のカード（枠を除いたもの）
        cands = []
        for page in ("1", "2", "3", "na"):
            im = grid.load(D + f"{key}_{page}.jpg")
            for b in grid.card_boxes(im, min_w=0.03, max_w=0.08):
                box = inset_frame(im, b)
                c = im.crop(box)
                cands.append((page, box, c, feat(c)))
        F = np.array([c[3] for c in cands])
        mine = [(k, e) for k, e in cur.items() if e["members"] == [name]]
        print(name, "表", len(cands), "アプリ", len(mine))
        for k, e in mine:
            old = Image.open(CARDS + e["file"])
            s = F @ feat(old)
            order = np.argsort(-s)
            best, second = float(s[order[0]]), float(s[order[1]])
            page, box, c, _ = cands[order[0]]
            new_w, old_w = min(c.size), min(old.size)
            ok = best >= TH and best - second >= MARGIN and new_w >= old_w * GAIN
            mb = min_block(old, c) if ok else 0.0
            ok = ok and mb >= BLOCK_TH
            report.append([name, e["collection"], e["source"], e["version"], round(best, 3), round(second, 3), round(mb, 3), old_w, new_w, "差し替え" if ok else ""])
            if ok and (e["collection"], name, e["source"], e["version"]) in DROP:
                ok = False
                report[-1][-1] = "透かしで外した"
            if ok:
                c = trim_pink(c)
                j.add(e["collection"], e["members"], e["source"], e["version"], c, "@idalshiro")
    j.save()
    with open(SP + "out/ida_hires_report.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["member", "collection", "source", "version", "best", "second", "min_block", "old_w", "new_w", "result"])
        w.writerows(report)
    print("差し替え", sum(1 for r in report if r[-1] == "差し替え"))
