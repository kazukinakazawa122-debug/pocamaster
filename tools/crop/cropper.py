"""一覧表の画像からカードの位置を見つけ、行（y）ごと・列（x）ごとに並べる"""
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage


def detect(path, work_w=1600, min_w=0.03, max_w=0.25, ratio=(1.2, 1.8), dark=225, satur=40):
    """カードらしい長方形（縦長）を探す。戻り値は元画像の座標"""
    im = Image.open(path).convert("RGB")
    s = work_w / im.width
    small = im.resize((work_w, int(im.height * s)))
    a = np.asarray(small).astype(int)
    mask = (a.mean(axis=2) < dark) | ((a.max(axis=2) - a.min(axis=2)) > satur)
    mask = ndimage.binary_opening(mask, iterations=2)
    mask = ndimage.binary_fill_holes(mask)
    lab, _ = ndimage.label(mask)
    boxes = []
    for sl in ndimage.find_objects(lab):
        h = sl[0].stop - sl[0].start
        w = sl[1].stop - sl[1].start
        if w < work_w * min_w or w > work_w * max_w:
            continue
        if ratio[0] < h / w < ratio[1]:
            boxes.append(tuple(int(v / s) for v in (sl[1].start, sl[0].start, sl[1].stop, sl[0].stop)))
    return im, boxes


def rows_of(boxes, tol=0.5):
    """y が近いものを同じ行にまとめ、行の中は x 順にする"""
    boxes = sorted(boxes, key=lambda b: (b[1] + b[3]) / 2)
    rows = []
    for b in boxes:
        cy = (b[1] + b[3]) / 2
        h = b[3] - b[1]
        if rows and abs(cy - rows[-1]["cy"]) < h * tol:
            rows[-1]["items"].append(b)
        else:
            rows.append({"cy": cy, "items": [b]})
    return [sorted(r["items"], key=lambda b: b[0]) for r in rows]


def preview(im, boxes, out, w=1200):
    p = im.copy()
    d = ImageDraw.Draw(p)
    for i, b in enumerate(boxes):
        d.rectangle(b, outline="red", width=max(3, im.width // 400))
        d.text((b[0] + 6, b[1] + 6), str(i), fill="red")
    p.thumbnail((w, w * 3))
    p.save(out, quality=80)


def crop(im, box, pad=0.0):
    x0, y0, x1, y1 = box
    return im.crop((x0, y0, x1, y1))
