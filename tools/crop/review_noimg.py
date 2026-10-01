"""画像のない枠の一覧ページ（人が見て「消す」「そのまま」を決める）
出力：public/_review/noimg_slots.html（Git には入れない）。コレクション → 入手元・バージョンごとに 1 行（メンバー別の画像なしは右に表示）"""
import base64, collections, csv, glob, html, io, json, os
from PIL import Image
from build2 import *

ORDER = ["ユジン", "ガウル", "レイ", "ウォニョン", "リズ", "イソ"]
if __name__ == "__main__":
    rows = list(csv.DictReader(open(PROJ + "public/seed/cards.csv", encoding="utf-8")))
    import zipfile
    # 画像があるかは、実際の ZIP（ID 入りの資料は入らない）の manifest で数える
    z = zipfile.ZipFile("C:/Users/kazuk/OneDrive/pocamaster-images/pocamaster-images.zip")
    cur = {(e["collection"], "/".join(sorted(e["members"])), e["source"], e["version"]): e for e in json.loads(z.read("manifest.json"))}
    groups = collections.OrderedDict()
    for r in rows:
        k = (r["collection"], r["source"], r["version"])
        e = cur.get((r["collection"], "/".join(sorted(r["member"].split("/"))), r["source"], r["version"]))
        g = groups.setdefault(k, {"no": [], "yes": []})
        (g["yes"] if e else g["no"]).append((r["member"], e))
    # 本人が「このまま（残す）」と決めた枠は一覧に出さない：IVE SECRET の StarRiver 2.0（実在するが出回りが少ない）
    KEEP_AS_IS = {("IVE SECRET", "StarRiver", "2.0")}
    items = [(k, g) for k, g in groups.items() if g["no"] and k not in KEEP_AS_IS]
    bycoll = collections.OrderedDict()
    for k, g in items:
        bycoll.setdefault(k[0], []).append((k, g))
    out = []; n = 0; index = []
    for coll, lst in bycoll.items():
        out.append(f'<h2>{html.escape(coll)} <span class="muted">画像なし {sum(len(g["no"]) for _, g in lst)} 枠・{len(lst)} 行</span></h2>')
        for k, g in lst:
            th = ""
            for m, e in g["yes"][:3]:
                im = Image.open(CARDS + e["thumb"]).convert("RGB"); im.thumbnail((50, 72)); f = io.BytesIO(); im.save(f, "JPEG", quality=60)
                th += f'<img title="{html.escape(m)}" src="data:image/jpeg;base64,{base64.b64encode(f.getvalue()).decode()}">'
            who = "・".join(m for m, _ in g["no"]) if len(g["no"]) < 6 else "全員"
            have = f'画像あり {len(g["yes"])}' if g["yes"] else "画像なし（全員）"
            out.append(f'<div class="row" id="r{n}"><div class="tx"><b>{html.escape(k[1])}</b> {html.escape(k[2])}<br><span class="muted">画像なし：{html.escape(who)}（{len(g["no"])}）・{have}</span></div><div class="th">{th}</div>'
                       f'<div class="btns"><button class="n" data-i="{n}">消す</button><button class="y" data-i="{n}">残す</button></div></div>')
            index.append([k[0], k[1], k[2], [m for m, _ in g["no"]]]); n += 1
    json.dump(index, open(SP + "noimg_index.json", "w", encoding="utf-8"), ensure_ascii=False)
    page = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>画像のない枠の整理</title><style>
:root{{--bg:#f5f0ed;--card:#fff;--line:#e3d3d5;--text:#3a2228;--muted:#7a5a62}}
@media (prefers-color-scheme:dark){{:root{{--bg:#111113;--card:#1c1c1f;--line:#2a2a2e;--text:#f4f4f5;--muted:#a1a1aa}}}}
body{{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,"Hiragino Sans","Yu Gothic UI",sans-serif}}
header{{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);padding:10px 16px;z-index:2;display:flex;gap:12px;align-items:center;flex-wrap:wrap}}
h1{{font-size:18px;margin:0}} h2{{font-size:16px;margin:18px 0 6px}} .muted{{color:var(--muted);font-size:12px;font-weight:400}}
main{{padding:4px 16px 80px;max-width:900px}}
.row{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px 10px;margin-bottom:6px;display:flex;gap:10px;align-items:center;font-size:14px}} .row.yes{{outline:3px solid #3FB56B}} .row.no{{outline:3px solid #E24B4A}}
.tx{{flex:1;min-width:0}} .th{{display:flex;gap:3px}} .th img{{width:34px;border-radius:4px}} .btns{{display:flex;gap:6px}}
button{{min-height:38px;padding:0 12px;border-radius:10px;border:1px solid var(--line);background:var(--bg);color:var(--text);font-weight:700;font-size:13px;cursor:pointer}}
button.y.on{{background:#3FB56B;color:#fff}} button.n.on{{background:#E24B4A;color:#fff}}
</style></head><body><header><h1>画像のない枠の整理</h1><span id="cnt" class="muted"></span><button id="copy">結果をコピー</button></header><main>{"".join(out)}</main><script>
const KEY='review_noimg'; let st={{}}; try{{st=JSON.parse(localStorage.getItem(KEY)||'{{}}')}}catch(e){{}}
function paint(){{document.querySelectorAll('.row').forEach(r=>{{const i=r.id.slice(1);r.classList.toggle('yes',st[i]==='y');r.classList.toggle('no',st[i]==='n');r.querySelector('.y').classList.toggle('on',st[i]==='y');r.querySelector('.n').classList.toggle('on',st[i]==='n')}});
const v=Object.values(st);document.getElementById('cnt').textContent='消す '+v.filter(x=>x==='n').length+'・残す '+v.filter(x=>x==='y').length+'・未 '+(document.querySelectorAll('.row').length-v.length);try{{localStorage.setItem(KEY,JSON.stringify(st))}}catch(e){{}}}}
document.addEventListener('click',e=>{{const b=e.target.closest('button[data-i]');if(!b)return;const i=b.dataset.i,v=b.classList.contains('y')?'y':'n';if(st[i]===v)delete st[i];else st[i]=v;paint()}});
document.getElementById('copy').onclick=()=>{{const g=k=>Object.keys(st).filter(x=>st[x]===k).sort((a,b)=>a-b).join(',')||'なし';const t='画像なし枠 消す: '+g('n')+' / 残す: '+g('y');if(navigator.clipboard)navigator.clipboard.writeText(t).then(()=>alert('コピーしました：'+t),()=>prompt('コピーしてください',t));else prompt('コピーしてください',t)}};
paint();</script></body></html>"""
    open(PROJ + "public/_review/noimg_slots.html", "w", encoding="utf-8").write(page)
    print(len(bycoll), "コレクション", n, "行", sum(len(g["no"]) for _, g in items), "枠")
