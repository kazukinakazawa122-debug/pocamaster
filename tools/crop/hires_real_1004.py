"""2026-10-03（3 回目）：本人が入れたフリマの実物の写真 31 枚（新しい資料 2026-10-03/フリマの実物の写真 3/）で画質を上げる。
12・13：6 枚セット（hires_real_1002 と同じ 3×2）、ほか：カード 1 枚の写真。hires_real_1003.py を土台に、この回の分だけにした。
本人の希望：明るさの補正はなし、彩度は上げる（SAT）
find：6 枚セットは hires_real_1002.find と同じ。1 枚の写真は、背景との色の差でカードの範囲を見つけ（detect）、全カードと比べて候補 10 枚 → 重ね合わせで決める。
→ review/1004/real_flea3.json"""
import glob, io, json, os, sys, zipfile
import numpy as np
from PIL import Image, ImageDraw
from build2 import *
from hires_real_0930 import locate, gray, ncc
import hires_real_1002 as H

sys.stdout.reconfigure(encoding="utf-8")
H.D = ROOT + "新しい資料 2026-10-03/フリマの実物の写真 3/"
H.OUTJ = SP + "review/1004/real_flea3.json"
SET_IDX = {12, 13}   # 6 枚セットの写真の番号（ほかはカード 1 枚）


def detect(im):
    """1 枚の写真：背景（まわりの色の中央値）との差が大きい部分の範囲（x0,y0,x1,y1）"""
    ox, oy, ex, ey = H.photo_box(im)   # 画面写真の白い余白をのぞく
    im = im.crop((ox, oy, ex, ey))
    W, Hh = im.size
    f = 200 / W
    a = np.asarray(im.resize((200, int(Hh * f)), Image.BILINEAR)).astype(float)
    h, w = a.shape[:2]
    m = int(min(h, w) * .05)
    border = np.concatenate([a[:m].reshape(-1, 3), a[-m:].reshape(-1, 3), a[:, :m].reshape(-1, 3), a[:, -m:].reshape(-1, 3)])
    bg = np.median(border, 0)
    d = np.linalg.norm(a - bg, axis=2)
    mask = d > max(35, np.percentile(d, 50))
    rows = np.where(mask.mean(1) > .35)[0]; cols = np.where(mask.mean(0) > .35)[0]
    if len(rows) == 0 or len(cols) == 0:
        return None
    return [ox + int(cols.min() / f), oy + int(rows.min() / f), ox + int((cols.max() + 1) / f), oy + int((rows.max() + 1) / f)]


def load():
    z = zipfile.ZipFile(H.ZIP)
    entries = [e for e in json.loads(z.read("manifest.json")) if not e.get("cover")]
    thumbs = [Image.open(io.BytesIO(z.read(e["thumb"]))).convert("RGB") for e in entries]
    return z, entries, thumbs


def find_sets(z, entries, thumbs, out):
    """6 枚セット（hires_real_1002.find と同じ）"""
    M = np.stack([H.desc(t) for t in thumbs])
    for pi, f in enumerate(H.photos()):
        if pi not in SET_IDX:
            continue
        im = Image.open(f).convert("RGB")
        x0, y0, x1, y1 = H.photo_box(im)
        cw, ch = (x1 - x0) / 3, (y1 - y0) / 2
        for r in range(2):
            for c in range(3):
                cell = (int(x0 + c * cw), int(y0 + r * ch), int(x0 + (c + 1) * cw), int(y0 + (r + 1) * ch))
                inner = im.crop((cell[0] + cw * .08, cell[1] + ch * .06, cell[2] - cw * .08, cell[3] - ch * .06))
                cands = np.argsort(-(M @ H.desc(inner)))[:10]
                best = None
                for k in cands:
                    old = Image.open(io.BytesIO(z.read(entries[k]["file"]))).convert("RGB")
                    box, sc = locate(im, cell, old, lo=0.6, hi=1.1)
                    if box and (best is None or sc > best[1]):
                        best = (int(k), sc, box)
                k, sc, box = best
                e = entries[k]
                out.append({"photo": os.path.basename(f), "pi": pi, "r": r, "c": c, "cell": cell, "box": box, "score": round(sc, 3),
                            "key": list(H.key(e)), "old_h": Image.open(io.BytesIO(z.read(e["file"]))).size[1], "alts": []})
                print(pi, r, c, round(sc, 3), H.key(e), "新", box[3] - box[1], "いま", out[-1]["old_h"], flush=True)
        json.dump(out, open(H.OUTJ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def find_singles(z, entries, thumbs, out):
    """カード 1 枚の写真：写真（白い余白をのぞく）を幅 100px にし、全カードの画像を 3 通りの大きさで動かして重なりを見る（上位 8 枚を決め直す）"""
    fs = H.photos()
    for pi in range(len(fs)):
        if pi in SET_IDX:
            continue
        im = Image.open(fs[pi]).convert("RGB")
        bx = H.photo_box(im)
        ph = im.crop(bx)
        f = 100 / ph.width
        g = gray(ph.resize((100, int(ph.height * f))))
        res = []
        for k, t in enumerate(thumbs):
            ar = t.height / t.width
            best = -2
            for w in (52, 64, 76):
                th = int(w * ar)
                if th >= g.shape[0] or w >= g.shape[1]:
                    continue
                best = max(best, float(ncc(g, gray(t.resize((w, th)))).max()))
            res.append(best)
        top = np.argsort(-np.array(res))[:8]
        best = None
        cell = (bx[0], bx[1], bx[2], bx[3])
        for k in top:
            old = Image.open(io.BytesIO(z.read(entries[int(k)]["file"]))).convert("RGB")
            box, sc = locate(im, cell, old, lo=0.4, hi=0.95)
            if box and (best is None or sc > best[1]):
                best = (int(k), sc, box)
        k, sc, box = best
        e = entries[k]
        out.append({"photo": os.path.basename(fs[pi]), "pi": pi, "r": 0, "c": 0, "cell": list(cell), "box": box, "score": round(sc, 3),
                    "key": list(H.key(e)), "old_h": Image.open(io.BytesIO(z.read(e["file"]))).size[1],
                    "alts": [list(H.key(entries[int(j)])) for j in top if int(j) != k][:3]})
        print(pi, round(sc, 3), H.key(e), "新", box[3] - box[1], "いま", out[-1]["old_h"], flush=True)
        json.dump(out, open(H.OUTJ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def find():
    os.makedirs(os.path.dirname(H.OUTJ), exist_ok=True)
    z, entries, thumbs = load()
    out = json.load(open(H.OUTJ, encoding="utf-8")) if os.path.exists(H.OUTJ) else []
    if not any(o["pi"] in SET_IDX for o in out):
        find_sets(z, entries, thumbs, out)
    out[:] = [o for o in out if o["pi"] in SET_IDX]   # 1 枚の写真は毎回やり直す
    find_singles(z, entries, thumbs, out)


# 使わない写真：12＝カードに「OLIVEYOUNG 6種コンプリート」の文字がかかる、
# 11＝店のバーコードのシールがカードにかかる（いまの画像は 600px 以上で、差し替えの利益もない）
NOT_USED = {13}   # 写真 13（6 枚セット。「hit」の小さなキャラの飾りつき）はアプリの画像に同じ写真がない。シリーズ待ち
# 本人の確認（2026-10-03）：確認ページの 65 組のうち #88（写真 23）だけ「ちがう」→ 差し替えない
NOT_USED_N = set()
H.FIX = {}                                  # 1002 のずれの直しは番号が別なので使わない
H.JOB = "zzzzzzzzzzzzzzzzzzzzz_real_flea_1004"  # 1002 よりあとに読まれる名前


# 本人に聞いて決まったシリーズ（2026-10-03）：0＝IVE SECRET Makestar 5.0（頭巾の 6 枚）。そのシリーズの 6 枚だけと重ね、6 マスと 6 人を 1 対 1 で決める
SERIES = {}


def series():
    import itertools
    out = json.load(open(H.OUTJ, encoding="utf-8"))
    z, entries, _ = load()
    files = H.photos()
    for pi, ser in SERIES.items():
        es = [e for e in entries if (e["collection"], e["source"], e["version"]) == ser]
        olds = [Image.open(io.BytesIO(z.read(e["file"]))).convert("RGB") for e in es]
        im = Image.open(files[pi]).convert("RGB")
        cells = [o for o in out if o["pi"] == pi]
        S = np.zeros((len(cells), len(es))); B = {}
        for i, o in enumerate(cells):
            for j, old in enumerate(olds):
                box, sc = locate(im, o["cell"], old, lo=0.6, hi=1.1)
                S[i, j] = sc if box else 0
                B[i, j] = box
        print(np.round(S, 2))
        best = max(itertools.permutations(range(len(es))), key=lambda p: sum(S[i, p[i]] for i in range(len(cells))))
        for i, o in enumerate(cells):
            j = best[i]
            print(" ", o["r"], o["c"], es[j]["members"], round(S[i, j], 3), "2 位", round(sorted(S[i])[-2], 3))
            o.update(key=list(H.key(es[j])), score=round(float(S[i, j]), 3), box=B[i, j], old_h=olds[j].size[1], series=True)
    json.dump(out, open(H.OUTJ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


# 写真 12（OLIVEYOUNG の帯がカードの上下の約 10% を隠す）：本人「下の段の 3 枚は切り取って使ってよい」（2026-10-03）。
# 帯の下から切る（上側が少し足りない）。箱は拡大した写真に目盛りを重ねてカードの角を読み取った。上の段 3 枚は使わない
MANUAL = {}


# 本人「先ほどの（写真 12 の 3 枚）も明るくして」（2026-10-03）：写真 12 は黒い衣装の暗い写真で、いまの画像と同じ明るさでは暗いので、
# 全体の平均（約 132/255）まで暗い部分を持ち上げる（箱の大きさで写真 12 のカードを見分ける）
SAT = float(os.environ.get("SAT", "1.2"))   # 彩度（本人「彩度を上げて」）。明るさの持ち上げはしない（前回「少し白っぽい」）


def _brighten(new, old):
    from PIL import ImageEnhance
    return ImageEnhance.Color(new).enhance(SAT)


H.brighten = _brighten


# 1 枚の写真で重なりが低かったもの：近くの写真と同じシリーズと見て、そのシリーズの全メンバーの画像と重ねて決め直す（顔では決めない）
SINGLE_SERIES = {2: ("IVE SECRET", "Beatroad", "2.0"), 10: ("IVE SECRET", "Soundwave", "5.0"),
                 15: ("IVE SECRET", "MusicArt", ""), 17: ("IVE SECRET", "MusicArt", "")}


def single_series():
    out = json.load(open(H.OUTJ, encoding="utf-8"))
    z, entries, _ = load()
    files = H.photos()
    for pi, ser in SINGLE_SERIES.items():
        es = [e for e in entries if (e["collection"], e["source"], e["version"]) == ser]
        o = next(o for o in out if o["pi"] == pi)
        im = Image.open(files[pi]).convert("RGB")
        res = []
        for e in es:
            old = Image.open(io.BytesIO(z.read(e["file"]))).convert("RGB")
            box, sc = locate(im, o["cell"], old, lo=0.4, hi=0.95)
            res.append((sc if box else 0, e, box, old.size[1]))
        res.sort(key=lambda r: -r[0])
        print(pi, ser, "前", o["key"][1], o["score"], "→", [(r[1]["members"][0], round(r[0], 3)) for r in res])
        sc, e, box, oh = res[0]
        if sc > o["score"]:
            o.update(key=list(H.key(e)), score=round(float(sc), 3), box=box, old_h=oh, series=True)
    json.dump(out, open(H.OUTJ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


# 斜めから撮った写真は、カードの四隅（左上・右上・右下・左下。写真の座標）を読み取って、まっすぐに直して切り取る（本人「24 がずれています」、2026-10-03）
# 写真 24：拡大した写真に目盛りを重ねて、辺を延ばした交点を読み取った。端から少し内側
QUAD = {24: [(315, 832), (952, 840), (996, 1890), (204, 1880)]}


def warp(im, quad, size):
    """四隅（左上・右上・右下・左下）を size の長方形に直す（遠近の補正）"""
    w, h = size
    src = np.array(quad, dtype=float)
    dst = np.array([(0, 0), (w, 0), (w, h), (0, h)], dtype=float)
    A = []
    for (x, y), (u, v) in zip(dst, src):   # 出力の点 (x,y) → 元の写真の点 (u,v)
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); A.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    c = np.linalg.solve(np.array(A), src.reshape(-1))
    return im.transform((w, h), Image.PERSPECTIVE, tuple(c), Image.BICUBIC)


def apply():
    """H.apply と同じ。ただし QUAD の写真は四隅からまっすぐに直して切り取る"""
    out = json.load(open(H.OUTJ, encoding="utf-8"))
    z = zipfile.ZipFile(H.ZIP)
    byk = {H.key(e): e for e in json.loads(z.read("manifest.json")) if not e.get("cover")}
    j = Job(H.JOB)
    ims = {}
    n_add = 0
    for n, o in enumerate(out):
        if o.get("skip"):
            continue
        if o["photo"] not in ims:
            ims[o["photo"]] = Image.open(H.D + o["photo"]).convert("RGB")
        im = ims[o["photo"]]
        if o["pi"] in QUAD:
            q = QUAD[o["pi"]]
            w = int(round((q[1][0] - q[0][0] + q[2][0] - q[3][0]) / 2)); h = int(round(w * 1.55))
            new = warp(im, q, (w, h))
        else:
            new = im.crop(tuple(o["box"]))
        k = o["key"]
        j.add(k[0], k[1].split("/"), k[2], k[3], H.brighten(new, None), "フリマの出品写真")
        n_add += 1
    j.save()
    print("差し替え", n_add)


def mark():
    """使わない写真・大きくならないものに skip を付け、確認ページには差し替えるものだけを出す"""
    out = json.load(open(H.OUTJ, encoding="utf-8"))
    z = zipfile.ZipFile(H.ZIP)
    entries = [e for e in json.loads(z.read("manifest.json")) if not e.get("cover")]
    for n, o in enumerate(out):
        if o["pi"] not in SET_IDX and o["score"] >= 0.55:
            o["series"] = True   # 1 枚の写真は、全カードから重ねて決めた 0.55 以上を使う（確認ページで目で見る）
        th = 0.55 if o.get("series") or o["pi"] not in SET_IDX else 0.75
        gain = (o["box"][3] - o["box"][1]) >= o["old_h"] * 1.15
        o["skip"] = o["pi"] in NOT_USED or n in NOT_USED_N or o["score"] < th or not gain
        if (o["pi"], o["r"], o["c"]) in MANUAL:
            o["box"] = MANUAL[o["pi"], o["r"], o["c"]]
            o["skip"] = False
    json.dump(out, open(H.OUTJ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    H.page(out, z, entries)
    print("差し替える", sum(not o["skip"] for o in out), "枚")


if __name__ == "__main__":
    {"single_series": single_series, "series": series, "mark": mark, "find": find, "refine": H.refine, "apply": apply}[sys.argv[1] if len(sys.argv) > 1 else "find"]()
