"""全体表（メンバーが列、特典が行）からカードを切り出す汎用ツール

使い方：
  cols = find_columns(im, x_range)       # 6 列の中心 x
  runs = find_rows(im, cols, card_w)     # 行ごとの (y0, y1)
"""
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage


def nonbg(a, dark=228, satur=35):
    return (a.mean(axis=2) < dark) | ((a.max(axis=2) - a.min(axis=2)) > satur)


def load(path):
    return Image.open(path).convert("RGB")


def card_boxes(im, work_w=1600, ratio=(1.2, 1.8), min_w=0.025, max_w=0.2):
    s = work_w / im.width
    small = im.resize((work_w, int(im.height * s)))
    m = nonbg(np.asarray(small).astype(int))
    m = ndimage.binary_opening(m, iterations=2)
    # 色付きの背景が白いパネルを囲んでいると、全体の穴埋めでパネルごと埋まってしまうので、
    # 穴埋めは 1 つずつの塊の中だけで行う
    lab, _ = ndimage.label(m)
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        h = sl[0].stop - sl[0].start
        w = sl[1].stop - sl[1].start
        if w < work_w * max_w:
            m[sl] |= ndimage.binary_fill_holes(lab[sl] == i)
    lab, _ = ndimage.label(m)
    out = []
    for sl in ndimage.find_objects(lab):
        h = sl[0].stop - sl[0].start
        w = sl[1].stop - sl[1].start
        if work_w * min_w < w < work_w * max_w and ratio[0] < h / w < ratio[1]:
            out.append(tuple(v / s for v in (sl[1].start, sl[0].start, sl[1].stop, sl[0].stop)))
    return out


def find_columns(im, x0, x1, n=6):
    """x0〜x1 の範囲にあるカードの中心 x を n 列にまとめる"""
    bs = [b for b in card_boxes(im) if x0 <= (b[0] + b[2]) / 2 <= x1]
    xs = np.array(sorted((b[0] + b[2]) / 2 for b in bs))
    w = float(np.median([b[2] - b[0] for b in bs]))
    # 単純な 1 次元 k-means
    c = np.linspace(xs.min(), xs.max(), n)
    for _ in range(30):
        lab = np.argmin(abs(xs[:, None] - c[None, :]), axis=1)
        c = np.array([xs[lab == k].mean() if (lab == k).any() else c[k] for k in range(n)])
    return sorted(c.tolist()), w


def find_rows(im, cols, w, min_members=4, min_h=None, y_from=0, y_to=None, gap=6):
    """各列の中心付近の細い帯を見て、カードがある y の範囲（行）を返す"""
    a = np.asarray(im).astype(int)
    H = a.shape[0]
    y_to = y_to or H
    band = max(4, int(w * 0.25))
    hits = []
    for x in cols:
        x = int(x)
        strip = nonbg(a[:, x - band // 2: x + band // 2]).mean(axis=1) > 0.5
        hits.append(strip)
    count = np.sum(hits, axis=0)
    on = count >= min_members
    on[:y_from] = False
    on[y_to:] = False
    on = ndimage.binary_closing(on, iterations=gap)
    lab, n = ndimage.label(on)
    runs = []
    min_h = min_h or w * 0.45
    for sl in ndimage.find_objects(lab):
        y0, y1 = sl[0].start, sl[0].stop
        if y1 - y0 >= min_h:
            runs.append((y0, y1))
    return runs


def preview(im, cols, w, runs, out, labels=None):
    p = im.copy()
    d = ImageDraw.Draw(p)
    lw = max(3, im.width // 500)
    for i, (y0, y1) in enumerate(runs):
        for x in cols:
            d.rectangle((x - w / 2, y0, x + w / 2, y1), outline="red", width=lw)
        d.text((cols[0] - w / 2 - 10, y0), str(i), fill="red")
    p.thumbnail((1400, 4000))
    p.save(out, quality=80)
