"""IVE SECRET の全員のカード（ぼかし）の切り出しの確認ページ（public/_review/secret_group.html。Git には入れない）"""
import base64, io, json
from PIL import Image, ImageDraw
from build2 import *
from albums_secret_group_add import D
def b64(img, w=300):
    img = img.convert("RGB"); img.thumbnail((w, w * 2)); f = io.BytesIO(); img.save(f, "JPEG", quality=85)
    return "data:image/jpeg;base64," + base64.b64encode(f.getvalue()).decode()
if __name__ == "__main__":
    out = json.load(open(SP + "out/zzzzzzzzzzzzzz_secret_group.json", encoding="utf-8"))["images"]
    by = {e["source"]: e for e in out}
    body = ""
    for f, box, src, title in (("MusicArt_告知_영풍문고.jpg", (598, 548, 764, 666), "MusicArt", "MusicArt｜全員（ピンクの告知）"), ("HOTTRACKS_교보문고.jpg", (852, 518, 1038, 806), "HOTTRACKS ラキドロ", "HOTTRACKS ラキドロ｜全員（赤いカード 7 枚）")):
        im = Image.open(D + f).convert("RGB"); an = im.copy(); ImageDraw.Draw(an).rectangle(box, outline=(230, 30, 60), width=4)
        e = by[src]; c = Image.open(CARDS + e["file"])
        body += f'<h2>{title}</h2><div class="row"><div><img class="big" src="{b64(an, 460)}"></div><div><img class="crop" src="{b64(c, 260)}"><br><span class="muted">切り出し結果 {c.size[0]}×{c.size[1]}px（アプリに入る画像）</span></div></div>'
    page = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SECRET 全員カードの確認</title><style>body{{margin:0;padding:16px;font-family:-apple-system,"Hiragino Sans","Yu Gothic UI",sans-serif;background:#f5f0ed;color:#3a2228}}h2{{font-size:15px;margin-top:22px}}.muted{{color:#7a5a62;font-size:12px}}.row{{display:flex;gap:18px;flex-wrap:wrap;align-items:flex-start}}.big{{max-width:420px;border-radius:8px;border:1px solid #e3d3d5}}.crop{{width:200px;border-radius:8px}}</style></head><body><h1 style="font-size:18px">IVE SECRET 全員のカード（ぼかし）の切り出し</h1><p class="muted">赤い枠が「ここを切り出した」位置です。右がアプリに入る画像です。</p>{body}</body></html>"""
    open(PROJ + "public/_review/secret_group.html", "w", encoding="utf-8").write(page); print("ok")
