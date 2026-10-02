"""2026-10-03：本人が入れたフリマの実物の写真 31 枚（新しい資料 2026-10-03/フリマの実物の写真 2/）で画質を上げる。
0〜12：6 枚セット（hires_real_1002 と同じ 3×2）、13〜30：カード 1 枚の写真。
find：6 枚セットは hires_real_1002.find と同じ。1 枚の写真は、背景との色の差でカードの範囲を見つけ（detect）、全カードと比べて候補 10 枚 → 重ね合わせで決める。
→ review/1003/real_flea2.json"""
import glob, io, json, os, sys, zipfile
import numpy as np
from PIL import Image, ImageDraw
from build2 import *
from hires_real_0930 import locate, gray, ncc
import hires_real_1002 as H

sys.stdout.reconfigure(encoding="utf-8")
H.D = ROOT + "新しい資料 2026-10-03/フリマの実物の写真 2/"
H.OUTJ = SP + "review/1003/real_flea2.json"
SET_N = 13   # 0〜12 が 6 枚セット


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
    for pi, f in enumerate(H.photos()[:SET_N]):
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
    for pi in range(SET_N, len(fs)):
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
    if not any(o["pi"] < SET_N for o in out):
        find_sets(z, entries, thumbs, out)
    out[:] = [o for o in out if o["pi"] < SET_N]   # 1 枚の写真は毎回やり直す
    find_singles(z, entries, thumbs, out)


# 使わない写真：12＝カードに「OLIVEYOUNG 6種コンプリート」の文字がかかる、
# 11＝店のバーコードのシールがカードにかかる（いまの画像は 600px 以上で、差し替えの利益もない）
NOT_USED = {11, 12}
# 本人の確認（2026-10-03）：確認ページの 65 組のうち #88（写真 23）だけ「ちがう」→ 差し替えない
NOT_USED_N = set()   # 以前は #88（写真 23）を「ちがう」としたが、本人に聞いて REVIVE+ リズ withmuu ラキドロ 9.0 と決まった（下の SINGLE）
H.FIX = {}                                  # 1002 のずれの直しは番号が別なので使わない
H.JOB = "zzzzzzzzzzzzzzzzzzzz_real_flea_1003"  # 1002 よりあとに読まれる名前


# 本人に聞いて決まったシリーズ（2026-10-03）：0＝IVE SECRET Makestar 5.0（頭巾の 6 枚）。そのシリーズの 6 枚だけと重ね、6 マスと 6 人を 1 対 1 で決める
SERIES = {0: ("IVE SECRET", "Makestar", "5.0")}


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
MANUAL = {(12, 1, 0): [8, 1410, 412, 1968], (12, 1, 1): [446, 1410, 836, 1976], (12, 1, 2): [898, 1410, 1246, 1962],
          # 写真 8（本人「切り取りがもう少し大きくとれます」、2026-10-03）：重ね合わせの範囲が、実際のカード（スリーブの内側）より内側だった
          # → 拡大した写真に目盛りを重ねてカードの端を読み取り、端から 6px 内側を切る（6 枚とも）
          (8, 0, 0): [44, 781, 412, 1349], (8, 0, 1): [453, 773, 819, 1341], (8, 0, 2): [858, 778, 1219, 1349],
          (8, 1, 0): [38, 1398, 419, 1984], (8, 1, 1): [468, 1398, 834, 1981], (8, 1, 2): [882, 1393, 1249, 1973]}


# 本人「先ほどの（写真 12 の 3 枚）も明るくして」（2026-10-03）：写真 12 は黒い衣装の暗い写真で、いまの画像と同じ明るさでは暗いので、
# 全体の平均（約 132/255）まで暗い部分を持ち上げる（箱の大きさで写真 12 のカードを見分ける）
_p12_sizes = {(b[2] - b[0], b[3] - b[1]) for k, b in MANUAL.items() if k[0] == 12}   # 写真 12 のカード（大きさで見分ける）
SAT_K = float(os.environ.get("SAT_K", "1.2"))   # 彩度：持ち上げの強さ（1−ガンマ）× SAT_K を足す。0 なら足さない
SAT_MAX = 1.4
# 本人「少し白っぽくなっているので、明るさは元に戻していい」（2026-10-03）→ 明るさ・彩度の補正をやめて、写真から切り取ったまま。補正がほしいときは True（LIFT・SAT_K・写真 12 の平均 132 で調整）
BRIGHTEN = False
LIFT = float(os.environ.get("LIFT", "0.6"))


def _lift(a, target):
    g = 1.0
    for cand in np.linspace(1.0, 0.5, 51):
        g = cand
        if (a ** cand).mean() >= target:
            break
    return g


def _brighten(new, old, p12=False):
    """いまの画像と同じ明るさまで暗い部分を持ち上げ（写真 12 は全体の平均まで）、持ち上げたぶん白っぽくなるので彩度を上げる（本人「少し白くなった」）"""
    from PIL import ImageEnhance
    if not BRIGHTEN:
        return new
    a = np.asarray(new.convert("RGB")).astype(np.float32) / 255
    target = 132 / 255 if p12 else np.asarray(old.convert("L")).mean() / 255
    if a.mean() >= target:
        return new
    if not p12:
        target = a.mean() + LIFT * (target - a.mean())   # いまの画像との差の LIFT 割まで（全部合わせると白っぽくかすむ。本人「少し白くなった」）
    g = _lift(a, target)
    img = Image.fromarray((255 * a ** g).clip(0, 255).astype(np.uint8))
    sat = min(SAT_MAX, 1 + (1 - g) * SAT_K)
    return ImageEnhance.Color(img).enhance(sat) if sat > 1.001 else img


H.brighten = lambda new, old: _brighten(new, old, new.size in _p12_sizes)


# 本人に聞いて決まった 1 枚の写真（2026-10-03）：23＝REVIVE+ リズ withmuu ラキドロ 9.0。そのカードの画像と重ねて範囲を決め直す
SINGLE = {23: ("REVIVE+", "リズ", "withmuu ラキドロ", "9.0")}


def single():
    out = json.load(open(H.OUTJ, encoding="utf-8"))
    z, entries, _ = load()
    files = H.photos()
    for pi, k in SINGLE.items():
        e = next(e for e in entries if H.key(e) == k)
        old = Image.open(io.BytesIO(z.read(e["file"]))).convert("RGB")
        o = next(o for o in out if o["pi"] == pi)
        im = Image.open(files[pi]).convert("RGB")
        box, sc = locate(im, o["cell"], old, lo=0.4, hi=0.95)
        print(pi, k, "前", o["key"], o["score"], "→ 重なり", round(sc, 3), box)
        o.update(key=list(k), score=round(float(sc), 3), box=box, old_h=old.size[1], series=True)
    json.dump(out, open(H.OUTJ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def mark():
    """使わない写真・大きくならないものに skip を付け、確認ページには差し替えるものだけを出す"""
    out = json.load(open(H.OUTJ, encoding="utf-8"))
    z = zipfile.ZipFile(H.ZIP)
    entries = [e for e in json.loads(z.read("manifest.json")) if not e.get("cover")]
    for n, o in enumerate(out):
        th = 0.55 if o.get("series") or o["pi"] >= SET_N else 0.75
        gain = (o["box"][3] - o["box"][1]) >= o["old_h"] * 1.15
        o["skip"] = o["pi"] in NOT_USED or n in NOT_USED_N or o["score"] < th or not gain
        if (o["pi"], o["r"], o["c"]) in MANUAL:
            o["box"] = MANUAL[o["pi"], o["r"], o["c"]]
            o["skip"] = False
    json.dump(out, open(H.OUTJ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    H.page(out, z, entries)
    print("差し替える", sum(not o["skip"] for o in out), "枚")


if __name__ == "__main__":
    {"single": single, "series": series, "mark": mark, "find": find, "refine": H.refine, "apply": H.apply}[sys.argv[1] if len(sys.argv) > 1 else "find"]()
