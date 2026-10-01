# 差分 ZIP を作る（本人の要望、2026-10-01「トレカが増えるたびに全部取り込むのは時間がかかる」）。
# merge.py で作った全部入りの ZIP（pocamaster-images.zip）を、前回この道具を実行したときの記録と比べ、
# 新しい画像・差し替えた画像だけを「差分 ZIP」にする。実行するたびに版の番号（No.1, 2, …）が 1 つ進む（変わっていなければ進まない）。
# 全部入りの ZIP にも info.json（いまの番号）を書き込む。アプリは取り込んだ番号を覚えて、取り込み忘れの差分を知らせる。
#
# 使い方：merge.py のあとに実行する
#   python tools/crop/make_diff.py
# できるもの：pocamaster-images/差分ZIP/pocamaster-差分-No<番号>-<日付>.zip、記録は 差分ZIP/history/snapshot-<番号>.json
import hashlib, json, os, sys, time, zipfile

# 試すときは環境変数 POCA_IMAGES で別のフォルダを指定できる
ROOT = os.environ.get("POCA_IMAGES", "C:/Users/kazuk/OneDrive/pocamaster-images/")
FULL = ROOT + "pocamaster-images.zip"
OUT = ROOT + "差分ZIP/"
HIST = OUT + "history/"

sys.stdout.reconfigure(encoding="utf-8")


def key(e):
    if e.get("cover"):
        return f"{e['collection']}|表紙"
    return "|".join([e["collection"], "+".join(sorted(e["members"])), e["source"], e["version"]])


def snapshots():
    if not os.path.isdir(HIST):
        return []
    return sorted(int(f[9:13]) for f in os.listdir(HIST) if f.startswith("snapshot-") and f.endswith(".json"))


with zipfile.ZipFile(FULL) as z:
    entries = json.loads(z.read("manifest.json"))
    names = set(z.namelist())
    now = {}
    for e in entries:
        h = hashlib.sha1()
        for f in (e["file"], e.get("thumb")):
            if f:
                h.update(z.read(f))
        h.update((e.get("credit") or "").encode())
        now[key(e)] = h.hexdigest()
    stamped = json.loads(z.read("info.json")) if "info.json" in names else None

os.makedirs(HIST, exist_ok=True)
seqs = snapshots()
last = seqs[-1] if seqs else 0
prev = json.load(open(HIST + f"snapshot-{last:04d}.json", encoding="utf-8")) if last else None
today = time.strftime("%Y-%m-%d")

if prev is None:
    # 初めて：いまの全部入りを No.1 にする（差分 ZIP は作らない）
    seq = 1
    print("初めての実行：いまの全部入りの ZIP を No.1 にしました（差分 ZIP はなし）")
else:
    changed = [e for e in entries if prev.get(key(e)) != now[key(e)]]
    gone = [k for k in prev if k not in now]
    if not changed:
        seq = last
        print(f"前回（No.{last}）から新しい画像・差し替えた画像はありません。差分 ZIP は作りません")
    else:
        seq = last + 1
        dp = OUT + f"pocamaster-差分-No{seq}-{today.replace('-', '')}.zip"
        with zipfile.ZipFile(FULL) as src, zipfile.ZipFile(dp, "w", zipfile.ZIP_STORED) as z:
            for e in changed:
                for f in (e["file"], e.get("thumb")):
                    if f:
                        z.writestr(f, src.read(f))
            z.writestr("manifest.json", json.dumps(changed, ensure_ascii=False))
            z.writestr("info.json", json.dumps({"kind": "diff", "seq": seq, "base": last, "date": today, "count": len(changed)}))
        new = sum(1 for e in changed if key(e) not in prev)
        print(f"差分 ZIP No.{seq}（No.{last} からの差分）：新しい画像 {new} 枚・差し替え {len(changed) - new} 枚 → {dp}（{os.path.getsize(dp) // 1024} KB）")
    if gone:
        # 差分 ZIP では画像を消せない（アプリには前の画像が残る）。消したいときは全部入りの ZIP では消えないので、アプリで個別に消す
        print(f"注意：前回あって今回ない画像 {len(gone)} 枚（差分 ZIP では消えません）：", "、".join(gone[:5]), "など" if len(gone) > 5 else "")

if seq != last:
    json.dump(now, open(HIST + f"snapshot-{seq:04d}.json", "w", encoding="utf-8"), ensure_ascii=False)

# 全部入りの ZIP に、いまの番号を書き込む（merge.py で作り直すと消えるので、そのたびにこの道具を実行する）
info = {"kind": "full", "seq": seq, "date": today, "count": len(entries)}
if not stamped or stamped.get("seq") != seq or stamped.get("count") != len(entries):
    if stamped is not None:
        # ZIP の中の 1 つのファイルだけは書き換えられないので、info.json を除いて作り直す
        tmp = FULL + ".tmp"
        with zipfile.ZipFile(FULL) as src, zipfile.ZipFile(tmp, "w", zipfile.ZIP_STORED) as z:
            for n in src.namelist():
                if n != "info.json":
                    z.writestr(src.getinfo(n), src.read(n))
            z.writestr("info.json", json.dumps(info))
        os.replace(tmp, FULL)
    else:
        with zipfile.ZipFile(FULL, "a", zipfile.ZIP_STORED) as z:
            z.writestr("info.json", json.dumps(info))
print(f"全部入りの ZIP：No.{seq}（{len(entries)} 枚）")
