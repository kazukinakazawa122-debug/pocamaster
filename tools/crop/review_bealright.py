"""Be Alright オフラインイベント（9.23・10.12 TOKYO）の切り出しと対応の確認ページ
出力：public/_review/bealright_offline.html（Git には入れない）。元の写真に枠と名前を重ねたものと、6 人分の「写真から切ったカード」と「アプリの画像」を並べる"""
import base64, glob, html, io, json
from PIL import Image, ImageDraw, ImageFont
from build2 import *
from albums_bealright_add import D, G, M
from hires_ida import feat

def b64(img, w=300):
    img = img.convert("RGB"); img.thumbnail((w, w * 2)); f = io.BytesIO(); img.save(f, "JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(f.getvalue()).decode()

if __name__ == "__main__":
    cur = {}
    for p in sorted(glob.glob(SP + "out/*.json")):
        for e in json.load(open(p, encoding="utf-8"))["images"]:
            if e["collection"] == "Be Alright" and len(e["members"]) == 1 and e["source"] == "オフラインイベント":
                cur[(e["members"][0], e["version"])] = e
    new = {(e["members"][0], e["version"]) for e in json.load(open(SP + "out/zzzzzzz_bealright_offline.json", encoding="utf-8"))["images"]}
    body = []
    try: font = ImageFont.truetype("C:/Windows/Fonts/meiryo.ttc", 54)
    except Exception: font = None
    for f, ver in (("offline_9.23_TOKYO.png", "9.23 TOKYO"), ("offline_10.12_TOKYO.png", "10.12 TOKYO")):
        cs, rs = G[f]; im = Image.open(D + f).convert("RGB"); an = im.copy(); d = ImageDraw.Draw(an)
        cells = []
        for i, m in enumerate(M):
            (x0, x1), (y0, y1) = cs[i % 3], rs[i // 3]
            d.rectangle((x0, y0, x1, y1), outline=(230, 30, 60), width=8); d.text((x0 + 14, y0 + 10), m, fill=(230, 30, 60), font=font)
            crop = im.crop((x0 + 4, y0 + 4, x1 - 4, y1 - 4)); old = cur.get((m, ver))
            sim = ""
            if old is not None and (m, ver) not in new:
                sim = f"（アプリの画像との似ている度合い {float(feat(crop) @ feat(Image.open(CARDS + old['file']))):.2f}）"
            tag = "新しく入れた" if (m, ver) in new else "すでにあった（比べるだけ）"
            cells.append(f'<div class="c"><b>{m}</b> <span class="muted">{tag}{sim}</span><div class="pair"><div><img src="{b64(crop, 220)}"><br>写真から</div>'
                         + (f'<div><img src="{b64(Image.open(CARDS + old["file"]), 220)}"><br>アプリ</div>' if old else '<div class="muted">アプリ：なし</div>') + '</div></div>')
        body.append(f'<h2>{ver}</h2><img class="big" src="{b64(an, 560)}"><div class="grid">{"".join(cells)}</div>')
    page = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Be Alright 切り出しの確認</title><style>
:root{{--bg:#f5f0ed;--card:#fff;--line:#e3d3d5;--text:#3a2228;--muted:#7a5a62}}@media (prefers-color-scheme:dark){{:root{{--bg:#111113;--card:#1c1c1f;--line:#2a2a2e;--text:#f4f4f5;--muted:#a1a1aa}}}}
body{{margin:0;padding:16px;background:var(--bg);color:var(--text);font-family:-apple-system,"Hiragino Sans","Yu Gothic UI",sans-serif}}h1{{font-size:18px}}h2{{font-size:16px;margin-top:24px}}.muted{{color:var(--muted);font-size:12px}}
.big{{max-width:280px;border-radius:8px;border:1px solid var(--line)}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px;margin-top:10px}}.c{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px}}
.pair{{display:flex;gap:8px;margin-top:6px;font-size:11px;text-align:center}}.pair img{{width:105px;border-radius:6px}}</style></head><body><h1>Be Alright オフラインイベントの切り出しと対応</h1>
<p class="muted">赤い枠と名前が「この位置のカードをこのメンバーとした」という印です。右の「アプリ」は、すでにアプリにあるカードで、写真から切ったカードと同じ写真かを比べるためのものです。</p>{"".join(body)}</body></html>"""
    open(PROJ + "public/_review/bealright_offline.html", "w", encoding="utf-8").write(page)
    print("ok")
