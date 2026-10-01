"""I've MINE 追加分（Malaysia のレイ・Taiwan 2・大阪城ホール 2/7）の切り出しの確認ページ
出力：public/_review/mine_add.html（Git には入れない）。元の写真に枠を重ねたものと、切り出したカードを並べる"""
import base64, html, io, json
from PIL import Image, ImageDraw
import grid
from build2 import *
from albums_mine_add import D, M

def b64(img, w=300):
    img = img.convert("RGB"); img.thumbnail((w, w * 2)); f = io.BytesIO(); img.save(f, "JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(f.getvalue()).decode()

if __name__ == "__main__":
    out = json.load(open(SP + "out/zzzzzzzz_mine_add.json", encoding="utf-8"))["images"]
    crops = {(e["source"], e["members"][0], e["version"]): Image.open(CARDS + e["file"]) for e in out}
    secs = []
    # Malaysia
    mal = Image.open(D + "Soundwave_ファンサイン_Malaysia_Rei.png").convert("RGB"); an = mal.copy(); ImageDraw.Draw(an).rectangle((222, 748, 1075, 1998), outline=(230, 30, 60), width=10)
    secs.append(("Soundwave ファンサイン Malaysia（レイ）", an, [("レイ", crops[("Soundwave ファンサイン", "レイ", "Malaysia")])]))
    # Taiwan 2
    t = Image.open(D + "Taiwan2_全員.jpg").convert("RGB"); an = t.copy(); d = ImageDraw.Draw(an)
    cs = [(52, 516), (519, 976), (980, 1437)]; rs = [(36, 742), (748, 1446)]
    for i, m in enumerate(M):
        (x0, x1), (y0, y1) = cs[i % 3], rs[i // 3]; d.rectangle((x0 + 3, y0 + 3, x1 - 3, y1 - 3), outline=(230, 30, 60), width=5); d.text((x0 + 12, y0 + 10), f"{i+1}:{m}", fill=(230, 30, 60))
    secs.append(("Taiwan 2（6 人）　※元の写真には名前がないので、並びは既存の画像との一致で決めた", an, [(m, crops[("Taiwan", m, "2")]) for m in M]))
    # Osaka
    o = grid.load(D + "会場限定特典_大阪城ホール_2-7_reina831wy.jpg"); an = o.copy(); d = ImageDraw.Draw(an)
    bs = sorted((b for b in grid.card_boxes(o, min_w=0.1, max_w=0.25, ratio=(1.3, 1.7)) if b[1] > 350), key=lambda b: (round((b[1] + b[3]) / 2 / 600), b[0]))
    order = ["ガウル", "ユジン", "レイ", "ウォニョン", "リズ", "イソ"]
    for m, b in zip(order, bs): d.rectangle(tuple(int(v) for v in b), outline=(30, 200, 60), width=6); d.text((b[0] + 12, b[1] + 10), m, fill=(30, 200, 60))
    secs.append(("会場限定特典 大阪城ホール 2/7（6 人）　※表の名札（GAEUL など）どおり", an, [(m, crops[("会場限定特典 大阪城ホール", m, "2/7")]) for m in order]))
    body = ""
    for title, an, cs_ in secs:
        body += f'<h2>{html.escape(title)}</h2><img class="big" src="{b64(an, 520)}"><div class="grid">' + "".join(f'<div class="c"><b>{m}</b><br><img src="{b64(c, 220)}"><br><span class="muted">{c.size[0]}×{c.size[1]}px</span></div>' for m, c in cs_) + "</div>"
    page = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I've MINE 切り出しの確認</title><style>
:root{{--bg:#f5f0ed;--card:#fff;--line:#e3d3d5;--text:#3a2228;--muted:#7a5a62}}@media (prefers-color-scheme:dark){{:root{{--bg:#111113;--card:#1c1c1f;--line:#2a2a2e;--text:#f4f4f5;--muted:#a1a1aa}}}}
body{{margin:0;padding:16px;background:var(--bg);color:var(--text);font-family:-apple-system,"Hiragino Sans","Yu Gothic UI",sans-serif}}h1{{font-size:18px}}h2{{font-size:15px;margin-top:26px}}.muted{{color:var(--muted);font-size:12px}}
.big{{max-width:300px;border-radius:8px;border:1px solid var(--line)}}.grid{{display:flex;flex-wrap:wrap;gap:10px;margin-top:10px}}.c{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px;font-size:13px;text-align:center}}.c img{{width:150px;border-radius:6px}}</style></head><body><h1>I've MINE 追加分の切り出しの確認</h1>
<p class="muted">元の写真の上の枠が「ここを切り出した」位置です。下の小さいカードが切り出した結果（アプリに入る画像）です。端が欠けていないか、背景や別のカードが写り込んでいないかを見てください。</p>{body}</body></html>"""
    open(PROJ + "public/_review/mine_add.html", "w", encoding="utf-8").write(page); print("ok")
