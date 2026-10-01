"""メンバー別の完全リスト：カードを読む順に並べ、番号付きのプレビューを作る"""
import sys, os, json
import numpy as np
from PIL import ImageDraw, ImageFont
import grid

SP = os.path.dirname(os.path.abspath(__file__)) + "/"
ROOT = r"C:/Users/kazuk/OneDrive/pocamaster-images/"
import re
# 番号で資料を指している（albums_*.py）。2026-10-01 に最上位へ日付名（20211223_…_iOS.jpg など）の @reina831wy の表が 58 枚入り（店舗ごとの表と同じもの）、
# 並びがずれたので除く。新しい資料は「新しい資料 <日付>/」に移すこと（番号がずれるため）
FILES = sorted(f for f in os.listdir(ROOT) if f.lower().endswith(".jpg") and not re.match(r"20\d{6}_\d+_iOS", f))


def ordered(path, ratio=(1.15, 1.8), min_w=0.03, max_w=0.12, y_min=0.0, tol=0.35, size_tol=(0.6, 1.5)):
    im = grid.load(path)
    bs = grid.card_boxes(im, ratio=ratio, min_w=min_w, max_w=max_w)
    bs = [b for b in bs if b[1] > im.height * y_min]
    if not bs:
        return im, []
    area = np.array([(b[2] - b[0]) * (b[3] - b[1]) for b in bs])
    med = np.median(area)
    bs = [b for b, a in zip(bs, area) if size_tol[0] * med < a < size_tol[1] * med]
    bs.sort(key=lambda b: (b[1] + b[3]) / 2)
    rows = []
    for b in bs:
        cy, h = (b[1] + b[3]) / 2, b[3] - b[1]
        if rows and abs(cy - rows[-1][0]) < h * tol:
            rows[-1][1].append(b)
        else:
            rows.append([cy, [b]])
    seq = [b for _, r in rows for b in sorted(r, key=lambda b: b[0])]
    return im, seq, [len(r) for _, r in rows]


def preview(im, seq, out):
    p = im.copy()
    d = ImageDraw.Draw(p)
    f = ImageFont.truetype("arial.ttf", max(24, im.width // 60))
    for i, b in enumerate(seq):
        d.rectangle(b, outline="red", width=max(3, im.width // 600))
        d.text((b[0] + 6, b[1] + 6), str(i), fill="yellow", font=f, stroke_width=3, stroke_fill="black")
    p.thumbnail((1800, 2400))
    p.save(out, quality=82)


if __name__ == "__main__":
    for a in sys.argv[1:]:
        i = int(a)
        im, seq, rows = ordered(ROOT + FILES[i])
        print(i, FILES[i], len(seq), rows)
        preview(im, seq, SP + f"ml_{i}.jpg")
