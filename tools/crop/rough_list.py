"""粗いカード（300px 未満）の一覧ページ用のデータを作る。
本人が自分で探すための一覧（PC とスマホで見る Artifact）。
  python tools/crop/rough_list.py <出力フォルダ>
出力：<出力フォルダ>/cards.json（カードの情報）・thumbs.json（今の画像の小さな版、data URI）
ページ本体は tools/crop/rough_list.html（出力フォルダにコピーする）。
"""
import base64, csv, io, json, os, shutil, sys, zipfile
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
SP = os.path.dirname(os.path.abspath(__file__)) + "/"
PROJ = SP + "../../"
ZIP = "C:/Users/kazuk/OneDrive/pocamaster-images/pocamaster-images.zip"
LOW = 300
MEMBERS = ["ユジン", "ガウル", "レイ", "ウォニョン", "リズ", "イソ"]


def mkey(names):
    if isinstance(names, str):
        names = [n for n in names.replace("・", "/").split("/") if n]
    if names == ["全員"]:
        names = MEMBERS
    return "+".join(sorted(names, key=MEMBERS.index))


def main(out):
    os.makedirs(out, exist_ok=True)
    ids = {}
    for r in csv.DictReader(open(PROJ + "public/seed/cards.csv", encoding="utf-8")):
        ids[(r["collection"], mkey(r["member"]), r["source"], r.get("version", ""))] = r["id"]
    nf = json.load(open(SP + "review/notfound.json", encoding="utf-8"))["cards"]
    nfk = {(c["collection"], mkey(c["members"]), c["source"], c["version"]): c.get("searched", "") for c in nf}
    z = zipfile.ZipFile(ZIP)
    info = json.loads(z.read("info.json")) if "info.json" in z.namelist() else {}
    cards, thumbs = [], {}
    for e in json.loads(z.read("manifest.json")):
        if e.get("cover"):
            continue
        data = z.read(e["file"])
        with Image.open(io.BytesIO(data)) as im:
            w, h = im.size
            if h >= LOW:
                continue
            k = (e["collection"], mkey(e["members"]), e["source"], e["version"])
            cid = ids.get(k) or "x" + str(len(cards))
            t = im.convert("RGB")
            t.thumbnail((240, 240), Image.LANCZOS)
            b = io.BytesIO()
            t.save(b, "JPEG", quality=72)
        mem = k[1].split("+")
        cards.append({
            "id": cid,
            "c": e["collection"],
            "m": "全員" if len(mem) == 6 else "・".join(mem),
            "s": e["source"],
            "v": e["version"],
            "w": w, "h": h,
            "nf": nfk.get(k, ""),
        })
        thumbs[cid] = "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
    order = {m: i for i, m in enumerate(MEMBERS)}
    cards.sort(key=lambda c: (c["c"], c["s"], c["v"], order.get(c["m"].split("・")[0], 9)))
    meta = {"made": info.get("seq", ""), "low": LOW, "count": len(cards)}
    json.dump({"meta": meta, "cards": cards}, open(out + "/cards.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    json.dump(thumbs, open(out + "/thumbs.json", "w", encoding="utf-8"), separators=(",", ":"))
    shutil.copy(SP + "rough_list.html", out + "/rough_list.html")
    mb = os.path.getsize(out + "/thumbs.json") / 1e6
    print(f"粗いカード {len(cards)} 枚 → {out}（thumbs.json {mb:.1f}MB）")


if __name__ == "__main__":
    main(sys.argv[1])
