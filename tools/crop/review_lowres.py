"""画質の低いカードの一覧ページを作る（本人の要望、2026-10-02「カード画像の画質はより良くする方針」）。
いま渡している全部入りの ZIP（pocamaster-images.zip）の画像の高さで数える。もっと大きな資料を探す目安にする。
出力：public/_review/lowres.html と public/_review/lowres/（見本の小さな画像。Git には入れない）
  python tools/crop/review_lowres.py
目安：iPhone で横 3 枚並びをきれいに見せるには高さ約 530px、拡大表示には約 1,400px が要る"""
import collections, html, io, json, os, shutil, sys, zipfile
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
ZIP = "C:/Users/kazuk/OneDrive/pocamaster-images/pocamaster-images.zip"
PROJ = r"C:/Users/kazuk/pocamaster/"
OUT = PROJ + "public/_review/lowres/"
VERY_LOW = 200  # これより低いと「とても粗い」
LOW = 300  # これより低いと「粗い」

z = zipfile.ZipFile(ZIP)
entries = json.loads(z.read("manifest.json"))
info = json.loads(z.read("info.json")) if "info.json" in z.namelist() else {}
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT)

by_col = collections.defaultdict(list)
total_by_col = collections.Counter()
for e in entries:
    if e.get("cover"):
        continue
    total_by_col[e["collection"]] += 1
    with Image.open(io.BytesIO(z.read(e["file"]))) as im:
        w, h = im.size
        if h >= LOW:
            continue
        # 見本：横 110px で表示するので、その 2 倍まで（小さい画像はそのまま）
        i = sum(len(v) for v in by_col.values())
        p = im.convert("RGB")
        p.thumbnail((220, 340))
        p.save(OUT + f"{i}.jpg", quality=82)
    by_col[e["collection"]].append({**e, "w": w, "h": h, "i": i})

cols = sorted(by_col, key=lambda c: (-len(by_col[c]), c))
n_low = sum(len(v) for v in by_col.values())
n_very = sum(1 for v in by_col.values() for e in v if e["h"] < VERY_LOW)
n_all = sum(total_by_col.values())


def esc(s):
    return html.escape(str(s))


summary = []
for k, c in enumerate(cols):
    v = by_col[c]
    very = sum(1 for e in v if e["h"] < VERY_LOW)
    # 粗いカードが多い資料の作者（同じ作者の大きな版を探すと、まとめて良くなる）
    credits = collections.Counter(e.get("credit") or "（不明）" for e in v).most_common(3)
    summary.append(
        f'<tr><td><a href="#c{k}">{esc(c)}</a></td><td class="n">{total_by_col[c]}</td><td class="n">{len(v)}</td>'
        f'<td class="n">{very}</td><td class="n">{round(len(v) * 100 / total_by_col[c])}%</td>'
        f'<td>{"、".join(f"{esc(a)}（{n}）" for a, n in credits)}</td></tr>'
    )

sections = []
for k, c in enumerate(cols):
    tiles = []
    for e in by_col[c]:
        very = e["h"] < VERY_LOW
        tiles.append(
            f'<div class="t{" very" if very else ""}" data-very="{1 if very else 0}"><img loading="lazy" src="lowres/{e["i"]}.jpg" alt="">'
            f'<div class="px">{e["w"]}×{e["h"]}</div><b>{esc("・".join(e["members"]))}</b><br>{esc(e["source"])} {esc(e["version"])}'
            f'<div class="cr">{esc(e.get("credit") or "")}</div></div>'
        )
    sections.append(f'<section><h2 id="c{k}">{esc(c)}<span>{len(by_col[c])} 枚</span></h2><div class="grid">{"".join(tiles)}</div></section>')

page = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>画質の低いカード</title><style>
:root{{--bg:#f4f4f2;--text:#1f1f1f;--muted:#6b6b68;--line:#dcdcd8;--warn:#b42318}}
@media (prefers-color-scheme:dark){{:root{{--bg:#111113;--text:#f4f4f5;--muted:#a1a1aa;--line:#2a2a2e;--warn:#f97066}}}}
body{{margin:0;background:var(--bg);color:var(--text);font:14px/1.5 -apple-system,"Hiragino Sans",sans-serif;padding:16px;max-width:1100px;margin:auto}}
h1{{font-size:20px;margin:0 0 4px}} p{{color:var(--muted);margin:4px 0 12px}}
table{{border-collapse:collapse;width:100%;font-size:13px;margin-bottom:12px}} th,td{{border-bottom:1px solid var(--line);padding:5px 6px;text-align:left;vertical-align:top}}
th{{color:var(--muted);font-weight:600}} td.n{{text-align:right;font-variant-numeric:tabular-nums}} a{{color:inherit}}
.bar{{position:sticky;top:0;background:var(--bg);padding:8px 0;border-bottom:1px solid var(--line);z-index:1}}
button{{font:inherit;padding:4px 12px;border-radius:999px;border:1px solid var(--line);background:var(--bg);color:var(--text)}} button.on{{background:var(--text);color:var(--bg)}}
h2{{font-size:16px;margin:24px 0 8px;display:flex;gap:8px;align-items:baseline}} h2 span{{color:var(--muted);font-size:12px;font-weight:600}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:10px}}
.t{{font-size:11px;line-height:1.35}} .t img{{width:100%;aspect-ratio:55/85;object-fit:cover;border-radius:5px;border:1px solid var(--line);display:block;background:var(--line)}}
.px{{font-weight:700;margin-top:3px}} .very .px{{color:var(--warn)}} .cr{{color:var(--muted)}}
.only-very .t:not(.very){{display:none}}
</style></head><body>
<h1>画質の低いカード</h1>
<p>全部入りの ZIP{(" No." + str(info["seq"])) if info.get("seq") else ""}（{n_all} 枚）のうち、高さ {LOW}px 未満が <b>{n_low} 枚</b>（そのうち {VERY_LOW}px 未満の「とても粗い」が {n_very} 枚）。
iPhone で横 3 枚並びをきれいに見せるには高さ約 530px、拡大表示には約 1,400px が要ります。
「資料の作者」は、粗いカードが多い作者（同じ作者のもっと大きな版や、店ごとの告知画像が見つかると、まとめて良くなります）。</p>
<table><tr><th>コレクション</th><th>全部</th><th>粗い</th><th>とても粗い</th><th>割合</th><th>資料の作者（粗い枚数）</th></tr>{"".join(summary)}</table>
<div class="bar"><button class="on" data-f="all">粗い（{LOW}px 未満）すべて</button> <button data-f="very">とても粗い（{VERY_LOW}px 未満）だけ</button></div>
<main>{"".join(sections)}</main>
<script>
document.querySelectorAll('.bar button').forEach(b => b.onclick = () => {{
  document.querySelectorAll('.bar button').forEach(x => x.classList.toggle('on', x === b));
  document.body.classList.toggle('only-very', b.dataset.f === 'very');
}});
</script></body></html>"""
open(PROJ + "public/_review/lowres.html", "w", encoding="utf-8").write(page)
print(f"粗い {n_low} 枚（とても粗い {n_very} 枚）／ {n_all} 枚、コレクション {len(cols)}")
