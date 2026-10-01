"""ALIVE・After LIKE・LOVE DIVE（Group Photocard）の切り出しの確認ページ（public/_review/alive_afterlike.html。Git には入れない）"""
import base64, io, json
from PIL import Image, ImageDraw
import grid
from build2 import *
from albums_alive_afterlike_add import D, M

def b64(img, w=300):
    img = img.convert("RGB"); img.thumbnail((w, w * 2)); f = io.BytesIO(); img.save(f, "JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(f.getvalue()).decode()

if __name__ == "__main__":
    out = json.load(open(SP + "out/zzzzzzzzzz_alive_afterlike.json", encoding="utf-8"))["images"]
    def cells(sel): return "".join(f'<div class="c"><b>{"・".join(e["members"])}</b><br><span class="muted">{e["version"]}</span><br><img src="{b64(Image.open(CARDS + e["file"]), 200)}"><br><span class="muted">{Image.open(CARDS + e["file"]).size[0]}×{Image.open(CARDS + e["file"]).size[1]}px</span></div>' for e in out if sel(e))
    body = ""
    # ALIVE
    k = 1284 / 693; im = Image.open(D + "ALIVE_会場限定盤.png").convert("RGB"); an = im.copy(); d = ImageDraw.Draw(an)
    cs = [(82, 262), (266, 447), (452, 636)]; rs = [(463, 737), (747, 1033)]
    for i, m in enumerate(M):
        (x0, x1), (y0, y1) = cs[i % 3], rs[i // 3]; yes = m in ("ウォニョン", "イソ")
        d.rectangle((int(x0 * k) + 3, int(y0 * k) + 3, int(x1 * k) - 3, int(y1 * k) - 3), outline=(230, 30, 60) if yes else (150, 150, 150), width=7 if yes else 3); d.text((int(x0 * k) + 12, int(y0 * k) + 10), f"{i+1}:{m}" + ("（入れた）" if yes else "（既存・確認用）"), fill=(230, 30, 60))
    body += f'<h2>ALIVE 会場限定盤（ウォニョン・イソを入れた。並びはアプリにある 4 枚と同じ写真で確認）</h2><img class="big" src="{b64(an.crop((0, 700, 1284, 2100)), 460)}"><div class="grid">{cells(lambda e: e["collection"]=="ALIVE")}</div>'
    # After LIKE
    s = grid.load(D + "AfterLIKE_musickorea_fansign_pvc_reina831wy.jpg"); an = s.copy(); d = ImageDraw.Draw(an)
    bs = sorted((b for b in grid.card_boxes(s, min_w=0.1, max_w=0.3, ratio=(1.3, 1.7)) if b[1] > 350), key=lambda b: (round((b[1] + b[3]) / 2 / 400), b[0]))
    for m, b in zip(["ガウル", "ユジン", "レイ", "ウォニョン", "リズ", "イソ"], bs): d.rectangle(tuple(int(v) for v in b), outline=(30, 200, 60), width=6); d.text((b[0] + 10, b[1] + 8), m, fill=(30, 200, 60))
    for n, (x0, y0, x1, y1) in enumerate([(412, 1430, 743, 1644), (779, 1430, 1111, 1644), (1144, 1430, 1477, 1644)], start=1): d.rectangle((x0, y0, x1, y1), outline=(30, 120, 220), width=6); d.text((x0 + 10, y0 + 8), f"GROUP {n}", fill=(30, 120, 220))
    body += f'<h2>After LIKE 「Music Korea ファンサイン当選特典 PVC」（表の名札どおり。緑＝メンバー、青＝全員のカード）</h2><img class="big" src="{b64(an, 520)}"><div class="grid">{cells(lambda e: e["collection"]=="After LIKE")}</div>'
    # LOVE DIVE
    ld = Image.open(ROOT + "新しい資料 2026-10-01/LOVE DIVE 追加分/LOVEDIVE_Jewel_9set_POB_group_reina831wy.jpg").convert("RGB"); an = ld.copy(); d = ImageDraw.Draw(an); k2 = 1996 / 1500
    for n, (x0, y0, x1, y1) in enumerate([(224, 922, 472, 1306), (522, 922, 770, 1306)], start=1): d.rectangle((int(x0 * k2) + 2, int(y0 * k2) + 2, int(x1 * k2) - 2, int(y1 * k2) - 2), outline=(230, 30, 60), width=8); d.text((int(x0 * k2) + 14, int(y0 * k2) + 10), f"Group {n}", fill=(230, 30, 60))
    body += f'<h2>LOVE DIVE 「Jewel ver. 9set POB」の Group Photocard 1・2（表の左＝1、右＝2）</h2><img class="big" src="{b64(an, 520)}"><div class="grid">{cells(lambda e: e["collection"]=="LOVE DIVE")}</div>'
    page = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ALIVE・After LIKE・LOVE DIVE の切り出しの確認</title><style>
body{{margin:0;padding:16px;font-family:-apple-system,"Hiragino Sans","Yu Gothic UI",sans-serif;background:#f5f0ed;color:#3a2228}}h2{{font-size:15px;margin-top:26px}}.muted{{color:#7a5a62;font-size:12px}}.big{{max-width:340px;border-radius:8px;border:1px solid #e3d3d5}}.grid{{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}}.c{{background:#fff;border:1px solid #e3d3d5;border-radius:10px;padding:8px;font-size:13px;text-align:center}}.c img{{width:130px;border-radius:6px}}</style></head><body><h1 style="font-size:18px">切り出しの確認（ALIVE・After LIKE・LOVE DIVE）</h1><p class="muted">枠が「ここを切り出した」位置です。下のカードが切り出し結果（アプリに入る画像）です。端の欠けや写り込みがないかを見てください。</p>{body}</body></html>"""
    open(PROJ + "public/_review/alive_afterlike.html", "w", encoding="utf-8").write(page); print("ok")
