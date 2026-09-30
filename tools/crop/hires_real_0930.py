"""本人が持ってきた実物のカードの写真（新しい資料 2026-09-30/実物の写真（本人、LUCID DREAM・REVIVE+ など）/、2026-09-30）で画質を上げる

- 写真の中のカードは 1 枚 約 300〜380px（いまの REVIVE+ 121px・LUCID DREAM 161px）。カードにお店・人の ID の透かしはない
- 1 回目はマス目で切ったため、カードの端が欠けたり隣が入ったりした（本人の指摘、2026-09-30）→ 切り直した：
  アプリにあるそのカードの画像（カード全体）を、大きさを変えながら写真の上で動かし、いちばん重なる位置（正規化相互相関）をカードの範囲とする
- 同じ写真だと目で確かめたもの（OK）だけ。位置：review/0930/real_photos.json（マスの位置・いちばん似ている枠）
- 確認用：out/real_0930_check.jpg（元の写真に切り取り範囲を描いたもの）
"""
import glob, json
import numpy as np
from PIL import Image, ImageDraw
from scipy.signal import fftconvolve
from build2 import *

D = ROOT + "新しい資料 2026-09-30/実物の写真（本人、LUCID DREAM・REVIVE+ など）/"
OK = {18, 19, 42, 48, 49, 50, 51, 52, 53, 60, 61, 62, 63, 64, 67, 70, 71, 72, 73, 74, 75, 76, 77, 90, 93, 94, 100, 102, 103, 105, 106,
      108, 110, 111, 112, 113, 115, 116, 117, 118, 119, 120, 121, 124, 126, 127, 128, 129, 130, 131, 133, 134, 136}


def gray(im):
    return np.asarray(im.convert("L")).astype(float)


def ncc(img, tpl):
    """正規化相互相関（valid）"""
    th, tw = tpl.shape
    t = tpl - tpl.mean(); tn = np.sqrt((t ** 2).sum()) + 1e-6
    num = fftconvolve(img, t[::-1, ::-1], mode="valid")
    c1 = np.cumsum(np.cumsum(np.pad(img, ((1, 0), (1, 0))), 0), 1)
    c2 = np.cumsum(np.cumsum(np.pad(img ** 2, ((1, 0), (1, 0))), 0), 1)
    def box(c):
        return c[th:, tw:] - c[:-th, tw:] - c[th:, :-tw] + c[:-th, :-tw]
    n = th * tw
    var = box(c2) - box(c1) ** 2 / n
    return num / (np.sqrt(np.maximum(var, 1e-6)) * tn)


def locate(photo, cell, old):
    """cell の周りで old（カード全体）がいちばん重なる範囲を探す。戻り値：(x0, y0, x1, y1), スコア"""
    cw, ch = cell[2] - cell[0], cell[3] - cell[1]
    pad = int(max(cw, ch) * 0.25)
    rx0, ry0 = max(0, cell[0] - pad), max(0, cell[1] - pad)
    rx1, ry1 = min(photo.width, cell[2] + pad), min(photo.height, cell[3] + pad)
    region = photo.crop((rx0, ry0, rx1, ry1))
    ar = old.height / old.width
    # 粗く探す（縮小）
    f = 160 / max(cw, 1)
    g = gray(region.resize((max(1, int(region.width * f)), max(1, int(region.height * f)))))
    best = (-2, None)
    for w in np.linspace(0.7 * cw, 1.15 * cw, 19):
        tw = int(w * f); th = int(w * ar * f)
        if tw < 20 or th >= g.shape[0] or tw >= g.shape[1]:
            continue
        s = ncc(g, gray(old.resize((tw, th))))
        k = np.unravel_index(s.argmax(), s.shape)
        if s[k] > best[0]:
            best = (s[k], (k[1] / f, k[0] / f, w))
    if best[1] is None:
        return None, -1
    x, y, w = best[1]
    # 細かく（元の大きさの半分で）
    f2 = 0.5
    sub = region.crop((max(0, int(x - 0.06 * cw)), max(0, int(y - 0.06 * cw)), min(region.width, int(x + w * 1.08 + 0.06 * cw)), min(region.height, int(y + w * ar * 1.08 + 0.06 * cw))))
    ox, oy = max(0, int(x - 0.06 * cw)), max(0, int(y - 0.06 * cw))
    g2 = gray(sub.resize((int(sub.width * f2), int(sub.height * f2))))
    best2 = (-2, None)
    for w2 in np.linspace(w * 0.95, w * 1.05, 11):
        tw = int(w2 * f2); th = int(w2 * ar * f2)
        if th >= g2.shape[0] or tw >= g2.shape[1]:
            continue
        s = ncc(g2, gray(old.resize((tw, th))))
        k = np.unravel_index(s.argmax(), s.shape)
        if s[k] > best2[0]:
            best2 = (s[k], (k[1] / f2, k[0] / f2, w2))
    sc, (x2, y2, w2) = best2 if best2[1] else best
    if best2[1] is None:
        x2, y2, w2 = x, y, w; ox = oy = 0
    X0 = rx0 + ox + x2; Y0 = ry0 + oy + y2
    return (int(X0), int(Y0), int(X0 + w2), int(Y0 + w2 * ar)), float(sc)


if __name__ == "__main__":
    res = json.load(open(SP + "review/0930/real_photos.json", encoding="utf-8"))
    cur = {}
    for p in sorted(glob.glob(SP + "out/*.json")):
        if "real_0930" in p:
            continue
        for e in json.load(open(p, encoding="utf-8"))["images"]:
            if len(e["members"]) == 1:
                cur[(e["collection"], e["members"][0], e["source"], e["version"])] = e["file"]
    j = Job("zzz_hires_real_0930"); ims = {}; found = {}
    for n in sorted(OK):
        r = res[n]
        if r["file"] not in ims:
            ims[r["file"]] = Image.open(D + r["file"]).convert("RGB")
        k = tuple(r["cands"][0][0])
        old = Image.open(CARDS + cur[k]).convert("RGB")
        box, sc = locate(ims[r["file"]], r["box"], old)
        found[n] = (box, sc)
        print(n, k[1], k[2], k[3], box, round(sc, 3))
        if box and sc >= 0.5 and min(box[2] - box[0], box[3] - box[1]) > min(old.size):
            j.add(k[0], [k[1]], k[2], k[3], ims[r["file"]].crop(box), "本人の写真")
    j.save()
    json.dump({str(n): v for n, v in found.items()}, open(SP + "review/0930/real_photos_found.json", "w"))
