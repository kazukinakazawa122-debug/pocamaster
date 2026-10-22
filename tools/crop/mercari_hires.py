"""メルカリ・X などの実物の写真（カード 1 枚ずつ）で、粗いカードの画質を上げる共通の道具（2026-10-23。hires_mercari_revive2〜4_1022.py をまとめたもの）
スキル .claude/skills/pocamaster-card-hires/SKILL.md の手順で使う。

資料：pocamaster-images/新しい資料 <日付>/<フォルダ>/ に、写真を「お店の名前_出品番号.jpg」で置く（保存は毎回本人の了承をとる）
設定：tools/crop/review/hires/<名前>.json（OK・TRIM・メモ。Claude が見比べて書く）
結果：tools/crop/review/hires/<名前>_find.json（照らし合わせ）、job は out/zzzzzzzzzzzzzzzzzzzzz_zz_<名前>.json（これまでの _y_・_z_mercari… の job より後、アプリの job〈z が 22 個〉より前に読まれる）

  python tools/crop/mercari_hires.py find   <名前> <資料のフォルダ> [コレクション]   … 写真ごとに、いちばん重なる枠を探す（1 件 10 秒ほど。裏で動かす）
  python tools/crop/mercari_hires.py sheet  <名前>     … 枠ごとにいちばん合う写真（0.68 以上・今より 1.15 倍以上）を、新旧を並べた画像にする（Claude が見る）
  python tools/crop/mercari_hires.py big    <名前>     … OK にしたものを大きく並べる（出品者の薄い透かし・端の背景を Claude が見る）
  python tools/crop/mercari_hires.py apply  <名前>     … OK のものを job に書く（このあと merge.py → make_diff.py）
  python tools/crop/mercari_hires.py review <名前>     … 本人に送る見比べの画像（JPEG）を pocamaster-images/メルカリ見比べ/<名前>_N.jpg に作る

<名前> は日付と通し番号にする（例 20261024a）。job は名前の順に読まれ、同じ枠ならあとの画像を使うので、あとの回ほど後ろになる名前にする。
"""
import glob, io, json, os, sys, zipfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from build2 import *
from hires_real_0930 import locate, gray, ncc
import hires_real_1002 as H

sys.stdout.reconfigure(encoding="utf-8")
CFG = SP + "review/hires/"
SCRATCH = ROOT + "メルカリ見比べ/"


def cfg(name):
    p = CFG + name + ".json"
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def found(name):
    return json.load(open(CFG + name + "_find.json", encoding="utf-8"))


def zipped():
    z = zipfile.ZipFile(ROOT + "pocamaster-images.zip")
    return z, [e for e in json.loads(z.read("manifest.json")) if not e.get("cover")]


def find(name, folder, collection=None):
    z, entries = zipped()
    if collection:
        entries = [e for e in entries if e["collection"] == collection]
    thumbs = [Image.open(io.BytesIO(z.read(e["thumb"]))).convert("RGB") for e in entries]
    os.makedirs(CFG, exist_ok=True)
    c = cfg(name); c.update(folder=folder, collection=collection); c.setdefault("ok", []); c.setdefault("trim", {})
    json.dump(c, open(CFG + name + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    out = []
    for f in sorted(glob.glob(ROOT + folder + "/*.jpg")):
        im = Image.open(f).convert("RGB")
        g = gray(im.resize((100, int(im.height * 100 / im.width))))
        res = []
        for t in thumbs:
            ar = t.height / t.width; best = -2
            for w in (40, 52, 64, 76):
                th = int(w * ar)
                if th < g.shape[0] and w < g.shape[1]:
                    best = max(best, float(ncc(g, gray(t.resize((w, th)))).max()))
            res.append(best)
        best = None
        for k in np.argsort(-np.array(res))[:8]:
            old = Image.open(io.BytesIO(z.read(entries[int(k)]["file"]))).convert("RGB")
            box, sc = locate(im, (0, 0, im.width, im.height), old, lo=0.3, hi=0.95)
            if box and (best is None or sc > best[1]):
                best = (int(k), sc, box)
        k, sc, box = best
        e = entries[k]
        out.append({"photo": os.path.basename(f), "box": box, "score": round(sc, 3), "key": list(H.key(e)),
                    "old_h": Image.open(io.BytesIO(z.read(e["file"]))).size[1]})
        print(len(out) - 1, os.path.basename(f)[:28], round(sc, 3), e["members"], e["source"], e["version"], "新", box[3] - box[1], "いま", out[-1]["old_h"], flush=True)
        json.dump(out, open(CFG + name + "_find.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def crops(name, ok=None):
    c, out = cfg(name), found(name)
    D = ROOT + c["folder"] + "/"
    res = []
    for n in (ok if ok is not None else c["ok"]):
        o = out[n]
        im = Image.open(D + o["photo"]).convert("RGB")
        box, _ = H.snap(im, o["box"], band=0.08)
        if str(n) in c["trim"]:
            l, t, r, b = c["trim"][str(n)]; w, h = box[2] - box[0], box[3] - box[1]
            box = [int(box[0] + w * l), int(box[1] + h * t), int(box[2] - w * r), int(box[3] - h * b)]
        res.append((n, o, im.crop(tuple(box))))
    return res


def candidates(name):
    out, best = found(name), {}
    for n, o in enumerate(out):
        if o["score"] < 0.68 or (o["box"][3] - o["box"][1]) < 1.15 * o["old_h"]:
            continue
        k = tuple(o["key"])
        if k not in best or o["score"] > out[best[k]]["score"]:
            best[k] = n
    return sorted(best.values())


def current(z, entries, key):
    return Image.open(io.BytesIO(z.read([e for e in entries if tuple(H.key(e)) == tuple(key)][0]["file"]))).convert("RGB")


def sheet(name):
    z, entries = zipped()
    sel = candidates(name); print("候補", len(sel), sel)
    f = ImageFont.truetype("meiryo.ttc", 15); tiles = []
    for n, o, new in crops(name, sel):
        old = current(z, entries, o["key"])
        t = Image.new("RGB", (330, 300), "white"); a = new.copy(); a.thumbnail((160, 250)); b = old.copy(); b.thumbnail((160, 250))
        t.paste(a, (0, 0)); t.paste(b, (168, 0)); d = ImageDraw.Draw(t)
        d.text((2, 252), f"#{n} {o['key'][1]} {o['score']}", fill="red", font=f); d.text((2, 272), f"{o['key'][2]} {o['key'][3]}"[:30], fill="black", font=f)
        tiles.append(t)
    os.makedirs(SCRATCH + "_作業", exist_ok=True)
    for p in range(0, len(tiles), 24):
        g = tiles[p:p + 24]; s = Image.new("RGB", (6 * 335, ((len(g) + 5) // 6) * 305), "white")
        for i, t in enumerate(g):
            s.paste(t, ((i % 6) * 335, (i // 6) * 305))
        s.save(SCRATCH + f"_作業/{name}_候補{p // 24 + 1}.jpg"); print(SCRATCH + f"_作業/{name}_候補{p // 24 + 1}.jpg")


def big(name):
    f = ImageFont.truetype("arial.ttf", 20); tiles = []
    for n, o, img in crops(name):
        t = img.resize((round(img.width * 520 / img.height), 520))
        ImageDraw.Draw(t).text((4, 4), f"{n} {img.size[1]}", fill=(255, 0, 0), font=f, stroke_width=2, stroke_fill=(255, 255, 255)); tiles.append(t)
    os.makedirs(SCRATCH + "_作業", exist_ok=True)
    for p in range(0, len(tiles), 6):
        g = tiles[p:p + 6]; s = Image.new("RGB", (sum(i.width + 6 for i in g), 520), "white"); x = 0
        for i in g:
            s.paste(i, (x, 0)); x += i.width + 6
        s.save(SCRATCH + f"_作業/{name}_大きく{p // 6 + 1}.jpg", quality=92); print(SCRATCH + f"_作業/{name}_大きく{p // 6 + 1}.jpg")


def apply(name):
    j = Job("zzzzzzzzzzzzzzzzzzzzz_zz_" + name)
    for n, o, img in crops(name):
        c, m, src, ver = o["key"]
        j.add(c, m.split("/"), src, ver, img, cfg(name).get("credit", "メルカリの出品写真"))
    j.save()


def review(name):
    # 「前の画像」は、この job を入れる前の画像（この job より前に読まれる job の最後の画像）
    me = "zzzzzzzzzzzzzzzzzzzzz_zz_" + name
    prev = {}
    for p in sorted(glob.glob(SP + "out/*.json")):
        if os.path.basename(p)[:-5] >= me:
            continue
        for e in json.load(open(p, encoding="utf-8")).get("images", []):
            prev[(e["collection"], "/".join(sorted(e["members"])), e["source"], e["version"])] = e
    f = ImageFont.truetype("meiryo.ttc", 26); fs = ImageFont.truetype("meiryo.ttc", 20); W, CH = 1080, 420; cells = []
    for i, (n, o, img) in enumerate(crops(name), 1):
        k = tuple(o["key"]); old = Image.open(CARDS + prev[k]["file"])
        c = Image.new("RGB", (W // 2, CH + 90), "white"); d = ImageDraw.Draw(c)
        for j, (im, lab) in enumerate(((img, "新しい写真"), (old, "前の画像"))):
            a = im.convert("RGB").copy(); a.thumbnail((W // 4 - 12, CH)); c.paste(a, (6 + j * (W // 4), 40)); d.text((6 + j * (W // 4), CH + 44), lab, fill=(110, 110, 110), font=fs)
        d.text((6, 4), f"#{i}", fill=(200, 0, 0), font=f); d.text((70, 8), f"{k[1]} {k[2]} {k[3]}"[:26], fill="black", font=fs); cells.append(c)
    os.makedirs(SCRATCH, exist_ok=True)
    for p in range(0, len(cells), 8):
        g = cells[p:p + 8]; s = Image.new("RGB", (W, ((len(g) + 1) // 2) * (CH + 90)), "white")
        for j, c in enumerate(g):
            s.paste(c, ((j % 2) * (W // 2), (j // 2) * (CH + 90)))
        s.save(SCRATCH + f"{name}_{p // 8 + 1}.jpg", quality=85); print(SCRATCH + f"{name}_{p // 8 + 1}.jpg")


if __name__ == "__main__":
    cmd, name = sys.argv[1], sys.argv[2]
    if cmd == "find":
        find(name, sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    else:
        {"sheet": sheet, "big": big, "apply": apply, "review": review}[cmd](name)
