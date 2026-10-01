"""枠のない余りの画像（グッズ「グッズ｜…」の切り出し）を見て、消すか残すかを決める確認ページを作る
出力：public/_review/goods_orphans.html（Git には入れない）。入手元ごとに「消す」「残す」を押す"""
import base64, collections, csv, glob, html, io, json, os
from PIL import Image
from build2 import *

if __name__ == "__main__":
    rows = list(csv.DictReader(open(PROJ + "public/seed/cards.csv", encoding="utf-8")))
    slots = {(r["collection"], "/".join(sorted(r["member"].split("/"))), r["source"], r["version"]) for r in rows}
    cur = {}
    for p in sorted(glob.glob(SP + "out/*.json")):
        for e in json.load(open(p, encoding="utf-8"))["images"]:
            cur[(e["collection"], "/".join(sorted(e["members"])), e["source"], e["version"])] = e
    groups = collections.OrderedDict()
    for k, e in cur.items():
        if k not in slots:
            groups.setdefault((k[0], k[2]), []).append((k, e))
    out = []
    for gi, ((coll, src), items) in enumerate(groups.items()):
        thumbs = []
        for k, e in items:
            im = Image.open(CARDS + e["thumb"]).convert("RGB"); im.thumbnail((120, 170))
            f = io.BytesIO(); im.save(f, "JPEG", quality=70)
            thumbs.append(f'<figure><img loading="lazy" src="data:image/jpeg;base64,{base64.b64encode(f.getvalue()).decode()}"><figcaption>{html.escape(k[1].replace("/", "・")[:12])} {html.escape(k[3][:14])}</figcaption></figure>')
        out.append(f'<section class="grp" id="r{gi}"><div class="hd"><b>{html.escape(src)}</b><span class="muted">{html.escape(coll[:40])}・{len(items)} 枚</span>'
                   f'<div class="btns"><button class="y" data-i="{gi}">残す</button><button class="n" data-i="{gi}">消す</button></div></div><div class="th">{"".join(thumbs)}</div></section>')
    page = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>余っている画像の確認</title><style>
:root{{--bg:#f5f0ed;--card:#fff;--line:#e3d3d5;--text:#3a2228;--muted:#7a5a62}}
@media (prefers-color-scheme:dark){{:root{{--bg:#111113;--card:#1c1c1f;--line:#2a2a2e;--text:#f4f4f5;--muted:#a1a1aa}}}}
body{{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,"Hiragino Sans","Yu Gothic UI",sans-serif}}
header{{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);padding:10px 16px;z-index:2;display:flex;gap:12px;align-items:center;flex-wrap:wrap}}
h1{{font-size:18px;margin:0}} .muted{{color:var(--muted);font-size:13px;margin-left:10px}}
main{{padding:12px 16px 80px;display:grid;gap:12px}}
.grp{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px}} .grp.yes{{outline:3px solid #3FB56B}} .grp.no{{outline:3px solid #E24B4A}}
.hd{{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-bottom:8px}} .btns{{margin-left:auto;display:flex;gap:6px}}
button{{min-height:40px;padding:0 14px;border-radius:10px;border:1px solid var(--line);background:var(--bg);color:var(--text);font-weight:700;font-size:14px;cursor:pointer}}
button.y.on{{background:#3FB56B;color:#fff}} button.n.on{{background:#E24B4A;color:#fff}}
.th{{display:flex;flex-wrap:wrap;gap:6px}} figure{{margin:0;width:100px;font-size:10px;text-align:center}} figure img{{width:100px;border-radius:6px;display:block}}
</style></head><body><header><h1>余っている画像の確認（グッズ）</h1><span id="cnt" class="muted"></span><button id="copy">結果をコピー</button></header><main>{"".join(out)}</main><script>
const KEY='review_goods'; let st={{}}; try{{st=JSON.parse(localStorage.getItem(KEY)||'{{}}')}}catch(e){{}}
function paint(){{document.querySelectorAll('.grp').forEach(r=>{{const i=r.id.slice(1);r.classList.toggle('yes',st[i]==='y');r.classList.toggle('no',st[i]==='n');r.querySelector('.y').classList.toggle('on',st[i]==='y');r.querySelector('.n').classList.toggle('on',st[i]==='n')}});
const v=Object.values(st);document.getElementById('cnt').textContent='残す '+v.filter(x=>x==='y').length+'・消す '+v.filter(x=>x==='n').length+'・未 '+(document.querySelectorAll('.grp').length-v.length);try{{localStorage.setItem(KEY,JSON.stringify(st))}}catch(e){{}}}}
document.addEventListener('click',e=>{{const b=e.target.closest('button[data-i]');if(!b)return;const i=b.dataset.i,v=b.classList.contains('y')?'y':'n';if(st[i]===v)delete st[i];else st[i]=v;paint()}});
document.getElementById('copy').onclick=()=>{{const g=k=>Object.keys(st).filter(x=>st[x]===k).sort((a,b)=>a-b).join(',')||'なし';const t='余り画像 消す: '+g('n')+' / 残す: '+g('y');if(navigator.clipboard)navigator.clipboard.writeText(t).then(()=>alert('コピーしました：'+t),()=>prompt('コピーしてください',t));else prompt('コピーしてください',t)}};
paint();</script></body></html>"""
    open(PROJ + "public/_review/goods_orphans.html", "w", encoding="utf-8").write(page)
    print(len(groups), "グループ", sum(len(v) for v in groups.values()), "枚")
