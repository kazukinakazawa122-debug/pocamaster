"""IVE SECRET の QQ Music 追加分の確認ページ（public/_review/secret_qq.html。Git には入れない）：どの写真をどのメンバーにしたか、切り出しの位置"""
import base64, io, json
from PIL import Image, ImageDraw
from build2 import *
from albums_secret_qq_add import D, BOX, WHO, k
def b64(img, w=300):
    img = img.convert("RGB"); img.thumbnail((w, w * 2)); f = io.BytesIO(); img.save(f, "JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(f.getvalue()).decode()
if __name__ == "__main__":
    out = json.load(open(SP + "out/zzzzzzzzzzzz_secret_qq.json", encoding="utf-8"))["images"]
    by = {(e["members"][0], e["version"]): e for e in out}
    body = ""
    for f, b in BOX.items():
        im = Image.open(D + f).convert("RGB"); an = im.copy(); ImageDraw.Draw(an).rectangle(tuple(int(v * k) for v in b), outline=(230, 30, 60), width=8)
        e = by[(WHO[f], "1")]
        body += f'<h2>{f} → <b>{WHO[f]}</b>（QQ Music 1）　<span class="muted">入れた順に レイ→リズ→イソ と見なした。違っていれば教えてください</span></h2><div class="row"><img class="big" src="{b64(an.crop((0, 700, 1284, 2100)), 360)}"><div><img class="crop" src="{b64(Image.open(CARDS + e["file"]), 260)}"><br><span class="muted">切り出し結果 {Image.open(CARDS + e["file"]).size[0]}px</span></div></div>'
    e = by[("ユジン", "Christmas")]
    body += f'<h2>Christmas_Yujin.jpg → <b>ユジン</b>（QQ Music × Starship Square｜Christmas）</h2><img class="crop" src="{b64(Image.open(CARDS + e["file"]), 260)}"> <span class="muted">{Image.open(CARDS + e["file"]).size[0]}×{Image.open(CARDS + e["file"]).size[1]}px（元の画像が小さい）</span>'
    page = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SECRET QQ Music の確認</title><style>body{{margin:0;padding:16px;font-family:-apple-system,"Hiragino Sans","Yu Gothic UI",sans-serif;background:#f5f0ed;color:#3a2228}}h2{{font-size:15px;margin-top:22px}}.muted{{color:#7a5a62;font-size:12px;font-weight:400}}.row{{display:flex;gap:16px;flex-wrap:wrap}}.big{{max-width:300px;border-radius:8px;border:1px solid #e3d3d5}}.crop{{width:200px;border-radius:8px}}</style></head><body><h1 style="font-size:18px">IVE SECRET QQ Music 追加分の確認</h1>{body}</body></html>"""
    open(PROJ + "public/_review/secret_qq.html", "w", encoding="utf-8").write(page); print("ok")
