"""本人が持ってきたフリマの出品写真（実物のカード 6 枚ずつ、iPhone の画面写真 11 枚）で画質を上げる（2026-10-02、本人の方針「画質はより良く」）
資料：新しい資料 2026-10-02/フリマの実物の写真/（「〜iOS 1.png」は同じ画像の重なりなので使わない）

1 段目（python tools/crop/hires_real_1002.py find）：
  写真の部分を見つけて 3 列 × 2 段のマスに分け、マスの真ん中の模様をいまの全部入りの ZIP の全カードと比べて候補を 10 枚にしぼり、
  候補ごとに写真の上で重ねて（hires_real_0930.locate、正規化相互相関）いちばん重なる枠とその範囲を決める。
  → review/1002/real_flea.json と public/_review/real_flea.html（本人が「同じ」「ちがう」を押す）。メンバーは顔では決めない（同じ写真かどうか）
2 段目（python tools/crop/hires_real_1002.py apply）：本人が「同じ」としたものだけ、いまの画像より大きければ差し替える
"""
import base64, glob, html, io, json, os, sys, zipfile
import numpy as np
from PIL import Image
from build2 import *
from hires_real_0930 import locate

sys.stdout.reconfigure(encoding="utf-8")
D = ROOT + "新しい資料 2026-10-02/フリマの実物の写真/"
ZIP = ROOT + "pocamaster-images.zip"
OUTJ = SP + "review/1002/real_flea.json"


def photos():
    return sorted(f for f in glob.glob(D + "*.png") if not f.endswith(" 1.png"))


def photo_box(im):
    """画面写真の中の写真の部分（白い背景でない行・列）"""
    a = np.asarray(im.convert("L")).astype(int)
    rows = np.where((a < 235).mean(1) > 0.5)[0]
    cols = np.where((a[rows.min():rows.max()] < 235).mean(0) > 0.5)[0]
    return int(cols.min()), int(rows.min()), int(cols.max()), int(rows.max())


def desc(im):
    """真ん中 70% の模様（明るさを正規化した 12×18）。写真の明るさの違いに強くする"""
    w, h = im.size
    g = np.asarray(im.convert("L").crop((w * .15, h * .15, w * .85, h * .85)).resize((12, 18), Image.BILINEAR)).astype(float).ravel()
    g -= g.mean()
    return g / (np.linalg.norm(g) + 1e-6)


def snap(im, box, band=0.12):
    """手本の画像に合わせた範囲（box）の近くで、実物のカードの端に合わせる（本人の指摘、2026-10-02「切り取りがずれている」）。
    手本（いまの画像）自体がカードの端と少しちがう範囲で切られているため、手本に合わせるとずれることがある。
    各辺について、辺の真ん中 60% の部分で明るさの変わり方がいちばん強い線を、±band の幅で探す。縦横の比が合わなければ元のまま"""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    g = np.asarray(im.convert("L")).astype(float)
    gx = np.abs(np.diff(g, axis=1))
    gy = np.abs(np.diff(g, axis=0))
    def best(lo, hi, score):
        lo, hi = max(1, int(lo)), int(hi)
        cand = [(score(v), v) for v in range(lo, hi)]
        return max(cand)[1] if cand else None
    ya, yb = int(y0 + h * .2), int(y1 - h * .2)
    xa, xb = int(x0 + w * .2), int(x1 - w * .2)
    L = best(x0 - w * band, x0 + w * band, lambda v: gx[ya:yb, min(v, gx.shape[1] - 1)].mean())
    R = best(x1 - w * band, min(x1 + w * band, gx.shape[1]), lambda v: gx[ya:yb, min(v, gx.shape[1] - 1)].mean())
    T = best(y0 - h * band, y0 + h * band, lambda v: gy[min(v, gy.shape[0] - 1), xa:xb].mean())
    B = best(y1 - h * band, min(y1 + h * band, gy.shape[0]), lambda v: gy[min(v, gy.shape[0] - 1), xa:xb].mean())
    if None in (L, R, T, B):
        return box, False
    nw, nh = R - L, B - T
    # カードの縦横の比は 54:86 ほど（0.63）。大きく外れたら（スリーブの端などを拾った）元のまま
    if not (0.58 < nw / max(nh, 1) < 0.69) or abs(nw - w) > w * 0.2 or abs(nh - h) > h * 0.2:
        return box, False
    return [int(L), int(T), int(R + 1), int(B + 1)], True


def key(e):
    return (e["collection"], "/".join(sorted(e["members"])), e["source"], e["version"])


def b64(im, w=150):
    im = im.convert("RGB").copy(); im.thumbnail((w, w * 2)); f = io.BytesIO(); im.save(f, "JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(f.getvalue()).decode()


def find():
    z = zipfile.ZipFile(ZIP)
    entries = [e for e in json.loads(z.read("manifest.json")) if not e.get("cover")]
    print("いまの画像", len(entries))
    thumbs = [Image.open(io.BytesIO(z.read(e["thumb"]))).convert("RGB") for e in entries]
    M = np.stack([desc(t) for t in thumbs])
    out = []
    for pi, f in enumerate(photos()):
        im = Image.open(f).convert("RGB")
        x0, y0, x1, y1 = photo_box(im)
        cw, ch = (x1 - x0) / 3, (y1 - y0) / 2
        for r in range(2):
            for c in range(3):
                cell = (int(x0 + c * cw), int(y0 + r * ch), int(x0 + (c + 1) * cw), int(y0 + (r + 1) * ch))
                inner = im.crop((cell[0] + cw * .08, cell[1] + ch * .06, cell[2] - cw * .08, cell[3] - ch * .06))
                sims = M @ desc(inner)
                cands = np.argsort(-sims)[:10]
                best = None
                for k in cands:
                    old = Image.open(io.BytesIO(z.read(entries[k]["file"]))).convert("RGB")
                    box, sc = locate(im, cell, old, lo=0.6, hi=1.1)
                    if box and (best is None or sc > best[1]):
                        best = (int(k), sc, box)
                k, sc, box = best
                e = entries[k]
                out.append({"photo": os.path.basename(f), "pi": pi, "r": r, "c": c, "cell": cell, "box": box, "score": round(sc, 3),
                            "key": list(key(e)), "old_h": Image.open(io.BytesIO(z.read(e["file"]))).size[1],
                            "alts": [list(key(entries[int(j)])) for j in cands[:5] if int(j) != k][:3]})
                print(pi, r, c, round(sc, 3), key(e), "新", box[3] - box[1], "いま", out[-1]["old_h"])
    os.makedirs(os.path.dirname(OUTJ), exist_ok=True)
    json.dump(out, open(OUTJ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    page(out, z, entries)


def page(out, z, entries):
    byk = {key(e): e for e in entries}
    ims = {}
    rows = []
    # 点数の高い順に並べる（番号 n は JSON の順のまま）。0.75 未満はちがうカードのことが多い
    for n, o in sorted(enumerate(out), key=lambda x: -x[1]["score"]):
        # 0.75 未満は目で見て全部ちがうカードだった（2026-10-02）→ 本人の手間を減らすため、ページに出さない
        # （シリーズで決め直したものは 0.7 以上なら出す）
        if o["score"] < (0.7 if o.get("series") else 0.75):
            continue
        if o["photo"] not in ims:
            ims[o["photo"]] = Image.open(D + o["photo"]).convert("RGB")
        new = ims[o["photo"]].crop(tuple(o["box"]))
        old = Image.open(io.BytesIO(z.read(byk[tuple(o["key"])]["file"])))
        k = o["key"]
        rows.append(
            f'<div class="row" id="r{n}"><div class="col"><img src="{b64(new)}">写真（高さ {o["box"][3] - o["box"][1]}px）</div>'
            f'<div class="col"><img src="{b64(old)}">いまの画像（{old.size[1]}px）</div>'
            f'<div class="col" style="width:190px;text-align:left">#{n}（写真 {o["pi"]}・{o["r"] + 1} 段 {o["c"] + 1} 列）<br>重なり <b style="color:{"#237A44" if o["score"] >= 0.75 else "#A32D2D"}">{o["score"]}</b>{"（ちがう可能性が高い）" if o["score"] < 0.75 else ""}<br>'
            f'<b>{html.escape(k[1])}</b><br>{html.escape(k[0])}<br>{html.escape(k[2])} {html.escape(k[3])}</div>'
            f'<div class="btns"><button class="y" data-i="{n}">同じ</button><button class="n" data-i="{n}">ちがう</button></div></div>')
    # 見た目とボタンの動きは前の見比べページ（leeseo_have.html）を使い、見出しと説明だけ今回用にする
    tpl = open(PROJ + "public/_review/leeseo_have.html", encoding="utf-8").read()
    import re
    head = re.sub(r"<title>.*?</title>", "<title>フリマの実物の写真の見比べ</title>", tpl[:tpl.index("<header>")])
    head += (f'<header><h1>フリマの実物の写真 {len(rows)} 枚</h1><span class="muted">左＝写真から切り出したカード、右＝いまアプリにあるそのカードの画像。'
             '同じ写真なら「同じ」、ちがうカード・切り出しがずれている・文字がかかっているなら「ちがう」（「同じ」だけ写真の画像に差し替えます）</span>'
             '<span id="cnt" class="muted"></span><button id="copy">結果をコピー</button></header><main>')
    tail = tpl[tpl.index("</main>"):].replace("イソ ちがう: ", "フリマ ちがう: ")
    open(PROJ + "public/_review/real_flea.html", "w", encoding="utf-8").write(head + "".join(rows) + tail)
    print("ページ", len(rows))


def refine():
    """2 回目：フリマの写真は同じシリーズの 6 枚をそろえて撮っていることが多い。点数の高い（0.75 以上）マスが 2 つ以上あるシリーズを
    その写真のシリーズとし（0.8 以上が 1 つでもよい）、ほかのマスを、そのシリーズでまだ使っていないメンバーの画像と 1 つずつ重ねて決め直す（顔では決めない）"""
    out = json.load(open(OUTJ, encoding="utf-8"))
    z = zipfile.ZipFile(ZIP)
    entries = [e for e in json.loads(z.read("manifest.json")) if not e.get("cover")]
    byk = {key(e): e for e in entries}
    import collections
    for pi in sorted({o["pi"] for o in out}):
        cells = [o for o in out if o["pi"] == pi]
        series = collections.Counter((o["key"][0], o["key"][2], o["key"][3]) for o in cells if o["score"] >= 0.75)
        # 2 枚以上そろっているか、とても高い（0.8 以上）カードが 1 枚あれば、その写真のシリーズとみなす
        strong = [o for o in cells if o["score"] >= 0.8]
        if not series or (series.most_common(1)[0][1] < 2 and not strong):
            continue
        ser = series.most_common(1)[0][0]
        im = Image.open(D + cells[0]["photo"]).convert("RGB")
        used = {o["key"][1] for o in cells if o["score"] >= 0.75 and (o["key"][0], o["key"][2], o["key"][3]) == ser}
        rest = [e for e in entries if (e["collection"], e["source"], e["version"]) == ser and "/".join(sorted(e["members"])) not in used]
        for o in cells:
            if o["score"] >= 0.75 and (o["key"][0], o["key"][2], o["key"][3]) == ser:
                continue
            best = None
            for e in rest:
                old = Image.open(io.BytesIO(z.read(e["file"]))).convert("RGB")
                box, sc = locate(im, o["cell"], old, lo=0.6, hi=1.1)
                if box and (best is None or sc > best[1]):
                    best = (e, sc, box)
            if best and best[1] > o["score"] - 0.05:
                e, sc, box = best
                print(pi, o["r"], o["c"], "シリーズで決め直し", key(e)[1], ser, round(sc, 3), "（前", o["key"][1], o["score"], "）")
                o.update(key=list(key(e)), score=round(sc, 3), box=box, old_h=Image.open(io.BytesIO(z.read(e["file"]))).size[1], series=True)
    json.dump(out, open(OUTJ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    page(out, z, entries)


# 本人の確認（2026-10-02）：ページの 36 組は全部「同じ」。#47・#29・#0 は「切り取りがずれている」
# → #47 は snap（カードの端に合わせる）、#29・#0 は snap がとなりのカード・スリーブの端を拾ったので、拡大した写真で角の位置を目で読み取った
FIX = {47: "snap", 29: [880, 1430, 1254, 1980], 0: [167, 865, 474, 1315]}
JOB = "zzzzzzzzzzzzzzzzzzz_real_flea_1002"  # ほかの job よりあとに読まれる名前（同じ枠なら、あとの画像を使う）


def brighten(new, old):
    """本人「新しい画像が少し暗い」→ いまの画像と同じくらいの明るさになるよう、暗い部分を持ち上げる（ガンマ。0.6〜1.0 の間）"""
    a = np.asarray(new.convert("RGB")).astype(np.float32) / 255
    target = np.asarray(old.convert("L")).mean() / 255
    cur = a.mean()
    if cur >= target:
        return new
    # 平均の明るさがいまの画像に近づくガンマを探す
    g = 1.0
    for cand in np.linspace(1.0, 0.6, 41):
        if (a ** cand).mean() >= target:
            g = cand
            break
        g = cand
    return Image.fromarray((255 * a ** g).clip(0, 255).astype(np.uint8))


def apply():
    out = json.load(open(OUTJ, encoding="utf-8"))
    z = zipfile.ZipFile(ZIP)
    byk = {key(e): e for e in json.loads(z.read("manifest.json")) if not e.get("cover")}
    j = Job(JOB)
    ims = {}
    n_add = 0
    for n, o in enumerate(out):
        if o["score"] < (0.7 if o.get("series") else 0.75):
            continue  # ページに出していない（ちがうカード）
        if o["photo"] not in ims:
            ims[o["photo"]] = Image.open(D + o["photo"]).convert("RGB")
        im = ims[o["photo"]]
        box = o["box"]
        if FIX.get(n) == "snap":
            box, _ = snap(im, box)
        elif n in FIX:
            box = FIX[n]
        if box[3] - box[1] < o["old_h"] * 1.15:
            continue  # 1.15 倍以上大きくならなければ、いまの画像（店の画像など）のまま
        old = Image.open(io.BytesIO(z.read(byk[tuple(o["key"])]["file"])))
        k = o["key"]
        j.add(k[0], k[1].split("/"), k[2], k[3], brighten(im.crop(tuple(box)), old), "フリマの出品写真")
        n_add += 1
        print(n, k, "高さ", o["old_h"], "→", box[3] - box[1])
    j.save()
    print("差し替え", n_add)


if __name__ == "__main__":
    {"find": find, "refine": refine, "apply": apply}[sys.argv[1] if len(sys.argv) > 1 else "find"]()
