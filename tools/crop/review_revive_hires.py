"""REVIVE+ の画質向上（hires_revive_wishlist.py）で差し替えた画像が、同じ写真か見比べるページを作る
出力：public/_review/revive_hires.html（Git には入れない）。左＝いまの画像、右＝wishlist の画像。「同じ」「ちがう」を押す"""
import base64, csv, glob, html, io, json, os
from PIL import Image
import grid
from build2 import *
from hires_revive_wishlist import D, EN, box

def b64(img, w=170):
    img = img.convert("RGB"); img.thumbnail((w, w * 2)); f = io.BytesIO(); img.save(f, "JPEG", quality=80)
    return "data:image/jpeg;base64," + base64.b64encode(f.getvalue()).decode()

if __name__ == "__main__":
    rep = json.load(open(SP + "out/zzzzzz_revive_wishlist_hires.json", encoding="utf-8"))["images"]
    pos = {(r["member"], r["source"], r["version"]): (int(r["row"]), int(r["col"])) for r in csv.DictReader(open(SP + "out/revive_wishlist_report.csv", encoding="utf-8-sig")) if r["result"]}
    cur = {}
    for p in sorted(glob.glob(SP + "out/*.json")):
        if os.path.basename(p) == "zzzzzz_revive_wishlist_hires.json":
            continue
        for e in json.load(open(p, encoding="utf-8"))["images"]:
            if e["collection"] == "REVIVE+" and len(e["members"]) == 1 and e["credit"] != "@powerofablink":
                cur[(e["members"][0], e["source"], e["version"])] = e
    sheets = {}
    rows = []; index = []
    for n_, e in enumerate(rep):
        m = e["members"][0]; k = (m, e["source"], e["version"])
        old = Image.open(CARDS + cur[k]["file"]); new = Image.open(CARDS + e["file"])
        rows.append(f'<div class="row" id="r{n_}"><div class="col"><img src="{b64(old)}">いまの画像（{min(old.size)}px）</div><div class="col"><img src="{b64(new)}">wishlist（{min(new.size)}px）</div>'
                    f'<div class="col" style="width:150px;text-align:left">#{n_} <b>{html.escape(m)}</b><br>{html.escape(e["source"])} {html.escape(e["version"])}</div>'
                    f'<div class="btns"><button class="y" data-i="{n_}">同じ</button><button class="n" data-i="{n_}">ちがう</button></div></div>')
        index.append([m, e["source"], e["version"]])
    json.dump(index, open(SP + "revive_hires_index.json", "w", encoding="utf-8"), ensure_ascii=False)
    page = open(PROJ + "public/_review/leeseo_have.html", encoding="utf-8").read()
    head = page[:page.index("<main>") + 6].replace("画像の見比べ（イソ）", "REVIVE+ 画質向上の見比べ"); tail = page[page.index("</main>"):]
    tail = tail.replace("イソ ちがう: ", "REVIVE+ ちがう: ")
    open(PROJ + "public/_review/revive_hires.html", "w", encoding="utf-8").write(head + "".join(rows) + tail)
    print(len(rows))
