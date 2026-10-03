"""アプリの「自分の画像を ZIP に書き出す」でできた ZIP（pocamaster-own-images-<日付>.zip）を、全部入りの画像 ZIP に入れる準備をする
（2026-10-03、アプリの改善 44.【2】）

使い方：
  1. アプリの設定で「自分の画像を ZIP に書き出す」→「ファイルに保存する」。できた ZIP を pocamaster-images/アプリから/ に置く
  2. python tools/crop/import_app_images.py            （アプリから/ の ZIP を全部）
     python tools/crop/import_app_images.py <ZIP のパス>  （1 つだけ）
  3. python tools/crop/merge.py → python tools/crop/make_diff.py（本人に渡すとき）

やること：ZIP の画像を _cards/zzzzzzzzzzzzzzzzzzzzzz_app_<ZIP の名前>/ に取り出し、out/ に job（画像の記録）を書く。
job の名前は、ほかの job よりあとに読まれるようにしてある（同じカードの画像があれば、アプリで切り取った画像を使う）。
初期データ（cards.csv）にない枠（アプリで自分で作ったカード）の画像は、入れずに一覧に出す。同じ ZIP をもう一度実行してもよい（作り直す）"""
import csv, glob, io, json, os, shutil, sys, zipfile

SP = os.path.dirname(os.path.abspath(__file__)) + "/"
PROJ = SP + "../../"
ROOT = "C:/Users/kazuk/OneDrive/pocamaster-images/"
CARDS = ROOT + "_cards/"
SRC = ROOT + "アプリから/"
sys.stdout.reconfigure(encoding="utf-8")


def slots():
    rows = csv.DictReader(open(PROJ + "public/seed/cards.csv", encoding="utf-8"))
    return {(r["collection"], "/".join(sorted(r["member"].split("/"))), r["source"], r["version"]) for r in rows}


def run(path, have):
    stem = os.path.splitext(os.path.basename(path))[0]
    name = "zzzzzzzzzzzzzzzzzzzzzz_app_" + stem
    z = zipfile.ZipFile(path)
    manifest = json.loads(z.read("manifest.json"))
    out_dir = CARDS + name + "/"
    shutil.rmtree(out_dir, ignore_errors=True)
    os.makedirs(out_dir)
    images, seed, missing = [], [], []
    for i, e in enumerate(manifest):
        key = (e["collection"], "/".join(sorted(e["members"])), e["source"], e["version"])
        if key not in have:
            missing.append(" / ".join(key))
            continue
        fn = f"{len(images):04d}"
        open(out_dir + fn + ".jpg", "wb").write(z.read(e["file"]))
        open(out_dir + fn + "_t.jpg", "wb").write(z.read(e["thumb"]))
        images.append({"collection": e["collection"], "members": e["members"], "source": e["source"], "version": e["version"],
                       "file": f"{name}/{fn}.jpg", "thumb": f"{name}/{fn}_t.jpg", "credit": e.get("credit") or "アプリで登録"})
        seed.append([e["collection"], "/".join(e["members"]), e["source"], e["version"]])
    json.dump({"seed": seed, "images": images}, open(SP + f"out/{name}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"{os.path.basename(path)}：画像 {len(images)} 枚を入れた（job {name}）")
    if missing:
        print(f"  初期データにない枠の画像 {len(missing)} 枚は入れていません（アプリで自分で作ったカード）：")
        for m in missing[:20]:
            print("   -", m)


if __name__ == "__main__":
    paths = sys.argv[1:] or sorted(glob.glob(SRC + "*.zip"))
    if not paths:
        print("ZIP がありません。アプリで書き出した ZIP を", SRC, "に置いてください")
        sys.exit(1)
    have = slots()
    for p in paths:
        run(p, have)
    print("次：python tools/crop/merge.py")
