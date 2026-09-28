"""表の画像から カードの枠（seed）と画像（manifest）を同時に作る

- overview(...)：メンバーが列・特典が行の全体表
- sheet6(...)：1 つの特典に 6 人分（2 段 × 3 列）が並んだ表
結果は scratchpad/out/<name>.json に保存し、merge.py でまとめる
"""
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
import grid

SP = os.path.dirname(os.path.abspath(__file__)) + "/"
PROJ = r"C:/Users/kazuk/pocamaster/"
ENG = "C:/Users/kazuk/OneDrive/pocamaster-images/IVE English ver. - photocard list-20260927T144026Z-1-001/IVE English ver. - photocard list/"
ROOT = "C:/Users/kazuk/OneDrive/pocamaster-images/"
CARDS = "C:/Users/kazuk/OneDrive/pocamaster-images/_cards/"
ORDER = ["ガウル", "ユジン", "レイ", "ウォニョン", "リズ", "イソ"]  # reina831wy の並び

os.makedirs(SP + "out", exist_ok=True)
SKIPPED = []


def trim(img):
    """周りの余白（白・薄い色）を切り落とす"""
    a = np.asarray(img).astype(int)
    m = grid.nonbg(a)
    m = ndimage.binary_opening(m, iterations=2)
    lab, n = ndimage.label(m)
    if n == 0:
        return img
    # いちばん大きい塊（カード本体）だけを残す。横に写り込んだ文字は捨てる
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    sl = ndimage.find_objects(lab)[int(np.argmax(sizes))]
    return img.crop((sl[1].start, sl[0].start, sl[1].stop, sl[0].stop))


class Job:
    def __init__(self, name):
        self.name = name
        self.seed = []      # (collection, member, source, version)
        self.images = []    # manifest entries
        self.n = 0

    def add(self, collection, members, source, version, img=None, credit="@reina831wy"):
        self.seed.append((collection, "/".join(members), source, version))
        if img is None:
            return
        d = CARDS + self.name + "/"
        os.makedirs(d, exist_ok=True)
        fn = f"{self.n:04d}"
        self.n += 1
        img = img.convert("RGB")
        img.thumbnail((800, 800))
        img.save(d + fn + ".jpg", quality=88)
        t = img.copy()
        t.thumbnail((400, 400))
        t.save(d + fn + "_t.jpg", quality=82)
        self.images.append({"collection": collection, "members": members, "source": source, "version": version,
                            "file": f"{self.name}/{fn}.jpg", "thumb": f"{self.name}/{fn}_t.jpg", "credit": credit})

    def save(self):
        json.dump({"seed": self.seed, "images": self.images}, open(SP + f"out/{self.name}.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=0)
        print(self.name, "seed", len(self.seed), "images", len(self.images))


def overview(job, path, collection, sides, y_from=0.05, order=ORDER, credit="@reina831wy"):
    """sides: [(cols or (x0,x1), [ (source, version) or None ... ]), ...]"""
    im = grid.load(path)
    for cols, labels in sides:
        if isinstance(cols, tuple):
            cols, w = grid.find_columns(im, *cols)
        else:
            w = (cols[-1] - cols[0]) / (len(cols) - 1) * 0.8
        runs = grid.find_rows(im, cols, w, y_from=int(im.height * y_from))
        if len(runs) < len(labels):
            print("SKIP", f"{collection}: 行が足りません {len(runs)} < {len(labels)}"); SKIPPED.append(f"{collection}: 行が足りません {len(runs)} < {len(labels)}"); return
        step = (cols[-1] - cols[0]) / (len(cols) - 1)
        for (y0, y1), lab in zip(runs, labels):
            if lab is None:
                continue
            src, ver = lab
            for x, mem in zip(cols, order):
                cell = im.crop((int(x - step * 0.48), y0, int(x + step * 0.48), y1))
                job.add(collection, [mem], src, ver, trim(cell), credit)


def seq_boxes(path, n, ratio=(1.2, 1.8), max_w=0.35):
    """表の中のカードを読む順に n 枚返す。見つからなければ None"""
    im = grid.load(path)
    bs = grid.card_boxes(im, ratio=ratio, max_w=max_w)
    if len(bs) < n:
        return None
    area = np.array([(b[2] - b[0]) * (b[3] - b[1]) for b in bs])
    med = np.median(sorted(area)[-n:])
    bs = [b for b, a in zip(bs, area) if 0.55 * med < a < 1.7 * med]
    bs.sort(key=lambda b: (b[1] + b[3]) / 2)
    rows = []
    for b in bs:
        cy, h = (b[1] + b[3]) / 2, b[3] - b[1]
        if rows and abs(cy - rows[-1][0]) < h * 0.4:
            rows[-1][1].append(b)
        else:
            rows.append([cy, [b]])
    seq = [b for _, r in rows for b in sorted(r, key=lambda b: b[0])]
    return seq if len(seq) == n else None


def sheet(job, path, collection, labels, order=ORDER, credit="@reina831wy", ratio=(1.2, 1.8), members=None, expect=None, max_w=0.35, template=None):
    """template：うまく見つからないとき、同じレイアウトの別の表のカード位置を使う"""
    k = len(labels)
    n = expect or k * len(members or order)
    seq = seq_boxes(path, n, ratio, max_w)
    if seq is None and template:
        seq = seq_boxes(template, n, ratio, max_w)
        if seq is not None:
            print("  template", path.split("/")[-1], "<-", template.split("/")[-1])
    if seq is not None:
        im = grid.load(path)
        who = members or [[m] for m in order]
        for i, b in enumerate(seq):
            src, ver = labels[i % k]
            job.add(collection, who[i // k], src, ver, im.crop(tuple(int(v) for v in b)), credit)
        return
    return _sheet_old(job, path, collection, labels, order, credit, ratio, members, expect, max_w)


def _sheet_old(job, path, collection, labels, order=ORDER, credit="@reina831wy", ratio=(1.2, 1.8), members=None, expect=None, max_w=0.35):
    """1 枚の表に、メンバー順に並んだカード。labels はメンバー 1 人あたりの (入手元, バージョン) の並び
    読む順番：上の段から、段の中は左から"""
    im = grid.load(path)
    bs = grid.card_boxes(im, ratio=ratio, max_w=max_w)
    k = len(labels)
    n = expect or k * len(members or order)
    if len(bs) < n:
        print("SKIP", f"{path}: カードが {len(bs)} 枚しか見つかりません（{n} 枚必要）"); SKIPPED.append(f"{path}: カードが {len(bs)} 枚しか見つかりません（{n} 枚必要）"); return
    area = np.array([(b[2] - b[0]) * (b[3] - b[1]) for b in bs])
    med = np.median(sorted(area)[-n:])
    bs = [b for b, a in zip(bs, area) if 0.55 * med < a < 1.7 * med]
    bs.sort(key=lambda b: (b[1] + b[3]) / 2)
    rows = []
    for b in bs:
        cy, h = (b[1] + b[3]) / 2, b[3] - b[1]
        if rows and abs(cy - rows[-1][0]) < h * 0.4:
            rows[-1][1].append(b)
        else:
            rows.append([cy, [b]])
    seq = [b for _, r in rows for b in sorted(r, key=lambda b: b[0])]
    if len(seq) != n:
        print("SKIP", f"{path}: 大きさのそろったカードが {len(seq)} 枚（{n} 枚のはず）"); SKIPPED.append(f"{path}: 大きさのそろったカードが {len(seq)} 枚（{n} 枚のはず）"); return
    who = members or [[m] for m in order]
    for i, b in enumerate(seq):
        src, ver = labels[i % k]
        job.add(collection, who[i // k], src, ver, im.crop(tuple(int(v) for v in b)), credit)


def sheet6(job, path, collection, source, version, order=ORDER, credit="@reina831wy", members=None, template=None):
    return sheet(job, path, collection, [(source, version)], order, credit, template=template)


def _old_sheet6(job, path, collection, source, version, order=ORDER, credit="@reina831wy", members=None):
    """6 人分が 2 段 × 3 列に並んだ表"""
    im = grid.load(path)
    bs = grid.card_boxes(im)
    if len(bs) < 6:
        print("SKIP", f"{path}: カードが {len(bs)} 枚しか見つかりません"); SKIPPED.append(f"{path}: カードが {len(bs)} 枚しか見つかりません"); return
    # 大きさがそろっている 6 枚を選ぶ
    area = np.array([(b[2] - b[0]) * (b[3] - b[1]) for b in bs])
    med = np.median(sorted(area)[-6:])
    bs = [b for b, a in zip(bs, area) if 0.6 * med < a < 1.6 * med]
    bs = sorted(bs, key=lambda b: b[1])
    rows = [sorted(bs[:3], key=lambda b: b[0]), sorted(bs[3:6], key=lambda b: b[0])]
    for b, mem in zip(rows[0] + rows[1], order):
        job.add(collection, members or [mem], source, version, im.crop(tuple(int(v) for v in b)), credit)


def sheet_chips(job, path, collection, labels, order=ORDER, credit="@reina831wy", members=None):
    """カードの下にあるメンバー名の札（GAEUL など）を目印にして切り出す。
    labels はメンバー 1 人あたりの (入手元, バージョン)。札 1 つの上に k 枚並ぶ"""
    im = grid.load(path)
    bs = grid.card_boxes(im, ratio=(0.15, 3.5), min_w=0.04, max_w=0.45)
    chips = [b for b in bs if 0.2 < (b[3] - b[1]) / (b[2] - b[0]) < 0.45]
    if chips:
        cw = np.median([b[2] - b[0] for b in chips])
        chips = [b for b in chips if abs((b[2] - b[0]) - cw) < cw * 0.15]
    need = len(members or order)
    if len(chips) != need:
        print("SKIP", path, "札の数", len(chips)); SKIPPED.append(f"{path}: 札 {len(chips)}"); return
    others = [b for b in bs if b not in chips]
    # 札の上にある一番大きいものをカードとみなし、幅・高さ・札との間隔を決める
    big = sorted(others, key=lambda b: -(b[2] - b[0]) * (b[3] - b[1]))
    k = len(labels)
    ref = big[: need * k]
    # 色の薄いカードは一部しか見つからないことがあるので、いちばん広いものを基準にする
    W = max(b[2] - b[0] for b in ref)
    H = max(b[3] - b[1] for b in ref if abs((b[2] - b[0]) - W) < W * 0.1)
    gaps = []
    for b in ref:
        below = [c for c in chips if c[1] > b[3] - 5 and abs((c[0] + c[2]) / 2 - (b[0] + b[2]) / 2) < W * k]
        if below and abs((b[3] - b[1]) - H) < H * 0.03:
            gaps.append(min(c[1] for c in below) - b[3])
    gap = np.median(gaps) if gaps else 12
    chips.sort(key=lambda c: (round((c[1] + c[3]) / 2 / (H * 0.5)), c[0]))
    who = members or [[m] for m in order]
    for ci, c in enumerate(chips):
        cx = (c[0] + c[2]) / 2
        bottom = c[1] - gap
        if k == 1:
            xs = [cx]
        else:
            near = [b for b in ref if abs(((b[0] + b[2]) / 2) - cx) < W * k and b[3] < c[1] + 5 and b[3] > c[1] - H * 0.6]
            xs = sorted((b[0] + b[2]) / 2 for b in near)
            if len(xs) != k:
                print("SKIP", path, "札", ci, "の上のカード", len(xs)); SKIPPED.append(f"{path}: 札 {ci}"); continue
        for (src, ver), x in zip(labels, xs):
            box = (int(x - W / 2), int(bottom - H), int(x + W / 2), int(bottom))
            job.add(collection, who[ci], src, ver, im.crop(box), credit)


def cols_from_row(im, y0, y1, x0, x1, n=6):
    """はっきり写っている段（y0〜y1）を横に見て、カードがある列の中心を n 個返す"""
    a = np.asarray(im.crop((int(x0), int(y0), int(x1), int(y1)))).astype(int)
    prof = grid.nonbg(a).mean(axis=0) > 0.6
    lab, k = ndimage.label(prof)
    runs = [(sl[0].start, sl[0].stop) for sl in ndimage.find_objects(lab)]
    runs = [r for r in runs if r[1] - r[0] > (x1 - x0) / (n * 3)]
    runs = sorted(runs, key=lambda r: -(r[1] - r[0]))[:n]
    return sorted(x0 + (s + e) / 2 for s, e in runs)


def fixed_grid(job, path, collection, cols, centers, labels, h, order=ORDER, credit="@reina831wy"):
    """列の中心 cols・段の中心 centers を決め打ちで切り出す（段の間隔が一定の表用）"""
    im = grid.load(path)
    step = (cols[-1] - cols[0]) / (len(cols) - 1)
    for cy, lab in zip(centers, labels):
        if lab is None:
            continue
        for x, mem in zip(cols, order):
            cell = im.crop((int(x - step * 0.48), int(cy - h / 2), int(x + step * 0.48), int(cy + h / 2)))
            job.add(collection, [mem], lab[0], lab[1], trim(cell), credit)


def cols_by_pitch(im, x0, x1, y0, y1, pitch, w, n=6):
    """列の間隔 pitch が分かっているとき、写真と一番よく重なる列の位置を探す"""
    a = np.asarray(im.crop((0, int(y0), im.width, int(y1)))).astype(int)
    p = grid.nonbg(a).mean(axis=0)
    best = None
    for s in range(int(x0), int(x1 - pitch * (n - 1))):
        cs = [s + pitch * k for k in range(n)]
        score = sum(p[int(c - w / 2): int(c + w / 2)].mean() for c in cs)
        if best is None or score > best[0]:
            best = (score, cs)
    return best[1]


def sheet_items(job, path, collection, items, ratio=(1.2, 1.8), credit="@reina831wy", max_w=0.35):
    """表の中のカードを読む順に items [(members, source, version), ...] に割り当てる"""
    seq = seq_boxes(path, len(items), ratio, max_w)
    if seq is None:
        print("SKIP", path, "items", len(items)); SKIPPED.append(path); return
    im = grid.load(path)
    for b, (mem, src, ver) in zip(seq, items):
        job.add(collection, mem, src, ver, im.crop(tuple(int(v) for v in b)), credit)


def member_lists(job, collection, files, labels, skip=0, credit="", **kw):
    """メンバー別の完全リスト。files={メンバー: 画像ファイル}、labels=読む順の (入手元, バージョン)。
    skip：先頭の余分な検出（見出し画像など）の数"""
    import memlist
    for mem, path in files.items():
        im, seq, rows = memlist.ordered(path, **kw)
        seq = seq[skip:]
        if len(seq) != len(labels):
            print("SKIP", mem, path.split("/")[-1], "found", len(seq), "need", len(labels), rows)
            SKIPPED.append(path)
            continue
        for b, (src, ver) in zip(seq, labels):
            job.add(collection, [mem], src, ver, im.crop(tuple(int(v) for v in b)), credit)
