"""直す・集める必要のあるカードを 1 つのページにまとめる（本人の要望、2026-10-15「粗い、差し替えが必要、画像がないものをまとめた資料」）。
いまの全部入りの ZIP（pocamaster-images.zip）と初期データ（public/seed/cards.csv）から作る。
- 画像なし：初期データの枠のうち、全部入りの ZIP に画像がない枠
- 差し替えが必要：
    ①本人が「画像がちがう」と言った枠（下の WRONG）
    ②同じ写真が別の枠にも入っている（重複。16×16 の dHash で距離 6 以内）
    ③ぼかしの画像（ほかに画像がないので仮に入れている見本）。tools/crop/review/blurred.json（目で確かめたもの）と、
      くっきり具合の数値（縦 120px にそろえたラプラシアンの分散）が BLUR_MAX 以下の画像（あとから増えた画像の分）
- 粗い：高さ 300px 未満。差し替えが必要なものは、そちらに出す
並び：コレクションごと（初期データの順）に、画像なし・差し替え・粗いをまぜて出す
出力：public/_review/todo.html（見本の小さな画像は public/_review/todo/。Git には入れない）と、
      スマホで見る 1 ファイル版（画像入り）を pocamaster-images/要対応カード一覧_スマホ用.html に
  python tools/crop/review_todo.py
"""
import base64, collections, csv, html, io, json, os, shutil, sys, zipfile
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
SP = os.path.dirname(os.path.abspath(__file__)) + "/"
PROJ = SP + "../../"
ROOT = "C:/Users/kazuk/OneDrive/pocamaster-images/"
ZIP = ROOT + "pocamaster-images.zip"
OUT = PROJ + "public/_review/todo/"
PHONE = ROOT + "要対応カード一覧_スマホ用.html"
LOW = 300
BLUR_MAX = 90
MEMBERS = ["ユジン", "ガウル", "レイ", "ウォニョン", "リズ", "イソ"]
COLOR = {"ユジン": "#378ADD", "ガウル": "#F08A3C", "レイ": "#F2C230", "ウォニョン": "#E85A9C", "リズ": "#3FB56B", "イソ": "#E24B4A"}
# 本人が「画像がちがう」と言った枠（コレクション・入手元・バージョン → 理由）
WRONG = {
    ("DIVE Official Fanclub｜ファンクラブ", "DIVE JAPAN 長期特典 2期", ""): "画像がちがう（本人、2026-10-06。本人が差し替える）",
}


def mkey(names):
    """メンバーを比べられる形に（「ユジン/ウォニョン」「全員」、名前の並び）"""
    if isinstance(names, str):
        names = [n for n in names.replace("・", "/").split("/") if n]
    if names == ["全員"]:
        names = MEMBERS
    return "+".join(sorted(names, key=MEMBERS.index))


def label(members_key):
    names = members_key.split("+")
    return "全員" if len(names) == len(MEMBERS) else "・".join(names)


def esc(s):
    return html.escape(str(s))


# --- 初期データの枠と、全部入りの ZIP の画像 ---
slots = [(r["collection"], mkey(r["member"]), r["source"], r.get("version", "")) for r in csv.DictReader(open(PROJ + "public/seed/cards.csv", encoding="utf-8"))]
z = zipfile.ZipFile(ZIP)
manifest = [e for e in json.loads(z.read("manifest.json")) if not e.get("cover")]
info = json.loads(z.read("info.json")) if "info.json" in z.namelist() else {}
by_key = {}
hashes = []
for e in manifest:
    k = (e["collection"], mkey(e["members"]), e["source"], e["version"])
    with Image.open(io.BytesIO(z.read(e["file"]))) as im:
        w, h = im.size
        g = im.convert("L")
        a = np.asarray(g.resize((17, 16), Image.BILINEAR), dtype=np.int16)
        hashes.append((k, (a[:, 1:] > a[:, :-1]).flatten()))
        b = np.asarray(g.resize((max(1, round(w * 120 / h)), 120), Image.LANCZOS), dtype=np.float32)
        lap = b[1:-1, 1:-1] * 4 - b[:-2, 1:-1] - b[2:, 1:-1] - b[1:-1, :-2] - b[1:-1, 2:]
    by_key[k] = {**e, "w": w, "h": h, "blur": float(lap.var())}

# --- 重複（同じ写真が別の枠に） ---
dup_of = {}
H = np.array([x[1] for x in hashes])
for i in range(len(hashes)):
    near = np.nonzero((H[i + 1:] != H[i]).sum(1) <= 6)[0]
    for j in near:
        a, b = hashes[i][0], hashes[i + 1 + j][0]
        if a == b:
            continue
        dup_of.setdefault(a, set()).add(b)
        dup_of.setdefault(b, set()).add(a)

# --- ぼかし ---
blurred = {(c["collection"], mkey(c["members"]), c["source"], c["version"]) for c in json.load(open(SP + "review/blurred.json", encoding="utf-8"))["cards"]}
# blurred.json は枠で決めているので、あとで本物の画像に差し替えた枠も残ってしまう（2026-10-23、メルカリの写真で KMONSTAR 1.0 を差し替えて気づいた）
# → くっきり具合が 300 より上なら外す（差し替えた画像は 379 以上。元のぼかしで 282 のもの〈REVIVE+ ガウル NY Music ラキドロ 2.0〉があったので 240 ではなく 300）
blurred = {k for k in blurred if k in by_key and by_key[k]["blur"] <= 300}
blurred |= {k for k, e in by_key.items() if e["blur"] <= BLUR_MAX}

# --- 分ける ---
none, replace, low = [], [], []
for k in dict.fromkeys(slots):  # 初期データの並び（同じ枠は 1 回）
    e = by_key.get(k)
    if not e:
        none.append({"k": k})
        continue
    reasons = []
    if (k[0], k[2], k[3]) in WRONG:
        reasons.append(WRONG[(k[0], k[2], k[3])])
    if k in dup_of:
        reasons.append("同じ写真が別の枠にもある：" + "、".join(f"{label(o[1])} {o[2]} {o[3]}".strip() for o in sorted(dup_of[k])))
    if k in blurred:
        reasons.append("ぼかしの画像（見本）")
    if reasons:
        replace.append({"k": k, "e": e, "why": reasons})
    elif e["h"] < LOW:
        low.append({"k": k, "e": e})

# --- 見本の小さな画像 ---
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT)
for n, x in enumerate(replace + low):
    with Image.open(io.BytesIO(z.read(x["e"]["file"]))) as im:
        p = im.convert("RGB")
        p.thumbnail((220, 340))
        p.save(OUT + f"{n}.jpg", quality=82)
    x["img"] = f"todo/{n}.jpg"


def tile(x, kind):
    c, mk, src, ver = x["k"]
    names = mk.split("+")
    border = COLOR[names[0]] if len(names) == 1 else "#8a8a86"
    if kind == "none":
        bg = COLOR[names[0]] + "40" if len(names) == 1 else "#e2e2de"
        pic = f'<div class="ph" style="border-color:{border};background:{bg}"><b>{esc(label(mk))}</b><span>{esc(src)}</span><span>{esc(ver)}</span></div>'
        note = '<div class="tag none">画像なし</div>'
    else:
        e = x["e"]
        pic = f'<img data-src="{x["img"]}" alt="" style="border-color:{border}">'
        size = f'<div class="tag">{"粗い " if kind == "low" else ""}{e["w"]}×{e["h"]}</div>'
        why = "".join(f'<div class="why">{esc(r)}</div>' for r in x.get("why", []))
        note = size + why + f'<div class="cr">{esc(e.get("credit") or "")}</div>'
    return f'<div class="t">{pic}<b>{esc(label(mk))}</b><br>{esc(src)} {esc(ver)}{note}</div>'


cols_order = [r["name"] for r in csv.DictReader(open(PROJ + "public/seed/collections.csv", encoding="utf-8"))]
# コレクションごとに、初期データの並びで（画像なし・差し替え・粗いをまぜる。本人の要望、2026-10-15「コレクション別で分けて」）
order = {k: i for i, k in enumerate(dict.fromkeys(slots))}
groups = collections.defaultdict(list)
for kind, lst in (("none", none), ("replace", replace), ("low", low)):
    for x in lst:
        groups[x["k"][0]].append((order[x["k"]], kind, x))
total_slots = collections.Counter(s[0] for s in dict.fromkeys(slots))
cols = sorted(groups, key=lambda c: cols_order.index(c) if c in cols_order else 999)
rows = "".join(
    f'<tr><td><a href="#c{n}">{esc(c)}</a></td><td class="n">{total_slots[c]}</td>'
    + "".join(f'<td class="n">{sum(1 for g in groups[c] if g[1] == kind) or ""}</td>' for kind in ("none", "replace", "low"))
    + f'<td class="n"><b>{len(groups[c])}</b></td></tr>'
    for n, c in enumerate(cols)
)
sections = [
    f'<details id="c{n}"><summary>{esc(c)}<span>{len(groups[c])} 枚</span></summary>'
    f'<div class="grid">{"".join(tile(x, kind) for _, kind, x in sorted(groups[c], key=lambda g: g[0]))}</div><a class="up" href="#top">↑ 表へ</a></details>'
    for n, c in enumerate(cols)
]

page = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>要対応カード一覧</title><style>
:root{{--bg:#f4f4f2;--text:#1f1f1f;--muted:#6b6b68;--line:#dcdcd8;--warn:#b42318;--panel:#ffffff}}
@media (prefers-color-scheme:dark){{:root{{--bg:#111113;--text:#f4f4f5;--muted:#a1a1aa;--line:#2a2a2e;--warn:#f97066;--panel:#1b1b1e}}}}
body{{margin:0 auto;background:var(--bg);color:var(--text);font:14px/1.5 -apple-system,"Hiragino Sans",sans-serif;padding:16px;max-width:1100px}}
h1{{font-size:20px;margin:0 0 4px}} p{{color:var(--muted);margin:4px 0 12px}}
table{{border-collapse:collapse;width:100%;font-size:13px;margin-bottom:12px}} th,td{{border-bottom:1px solid var(--line);padding:5px 6px;text-align:left;vertical-align:top}}
th{{color:var(--muted);font-weight:600}} td.n,th.n{{text-align:right;font-variant-numeric:tabular-nums}} a{{color:inherit}}
details{{border-top:1px solid var(--line)}} details:last-of-type{{border-bottom:1px solid var(--line)}}
summary{{font-size:16px;font-weight:700;padding:12px 2px;display:flex;gap:8px;align-items:baseline;cursor:pointer;list-style:none;scroll-margin-top:8px}}
summary::-webkit-details-marker{{display:none}} summary::before{{content:"▸";color:var(--muted)}} details[open] summary::before{{content:"▾"}}
summary span{{color:var(--muted);font-size:12px;font-weight:600}}
.up{{display:block;text-align:right;font-size:12px;color:var(--muted);text-decoration:none;padding:10px 2px 14px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:10px}}
.t{{font-size:11px;line-height:1.35}}
.t img,.t .ph{{width:100%;aspect-ratio:55/85;object-fit:cover;border-radius:5px;border:2px solid;display:block;box-sizing:border-box;margin-bottom:3px}}
.t .ph{{display:flex;flex-direction:column;justify-content:center;align-items:center;gap:2px;text-align:center;padding:4px;color:var(--text)}}
.tag{{font-weight:700}} .tag.none,.why{{color:var(--warn)}} .cr{{color:var(--muted)}}
</style></head><body id="top">
<h1>要対応カード一覧</h1>
<p>全部入りの ZIP{(" No." + str(info["seq"])) if info.get("seq") else ""}（{info.get("date", "")}）と初期データ（{len(dict.fromkeys(slots))} 枠）から作りました。
画像なし <b>{len(none)} 枠</b>・差し替えが必要 <b>{len(replace)} 枚</b>・粗い <b>{len(low)} 枚</b>（高さ {LOW}px 未満）。
コレクション名を押すと、そのコレクションのカードが開きます（開いたものだけ画像を読むので軽い）。「資料の作者」は、同じ作者のもっと大きな版を探す手がかりです。</p>
<table><tr><th>コレクション</th><th class="n">枠</th><th class="n">画像なし</th><th class="n">差し替え</th><th class="n">粗い</th><th class="n">合計</th></tr>{rows}</table>
<main>{"".join(sections)}</main>
<script>
function show(d) {{ d.querySelectorAll('img[data-src]').forEach(i => {{ i.src = i.dataset.src; i.removeAttribute('data-src'); }}); }}
document.querySelectorAll('details').forEach(d => d.addEventListener('toggle', () => d.open && show(d)));
function go() {{ const d = location.hash && document.querySelector(location.hash); if (d && d.tagName === 'DETAILS') {{ d.open = true; d.scrollIntoView(); }} }}
addEventListener('hashchange', go); go();
</script>
</body></html>"""
open(PROJ + "public/_review/todo.html", "w", encoding="utf-8").write(page)


# --- スマホで見る 1 ファイル版（画像を中に入れる。少し小さく・軽く） ---
def inline(m):
    with Image.open(PROJ + "public/_review/" + m) as im:
        p = im.convert("RGB")
        p.thumbnail((150, 232))
        buf = io.BytesIO()
        p.save(buf, "JPEG", quality=60)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


phone = page
for x in replace + low:
    phone = phone.replace(f'data-src="{x["img"]}"', f'data-src="{inline(x["img"])}"', 1)
open(PHONE, "w", encoding="utf-8").write(phone)
print(f"画像なし {len(none)} 枠・差し替えが必要 {len(replace)} 枚・粗い {len(low)} 枚／ 枠 {len(dict.fromkeys(slots))}・画像 {len(manifest)}")
print("内訳（差し替え）", collections.Counter(("ちがう" if any("ちがう" in r for r in x["why"]) else "") + ("重複" if any("同じ写真" in r for r in x["why"]) else "") + ("ぼかし" if any("ぼかし" in r for r in x["why"]) else "") for x in replace))
print("出力", PROJ + "public/_review/todo.html", "／", PHONE, round(os.path.getsize(PHONE) / 1e6, 1), "MB")
