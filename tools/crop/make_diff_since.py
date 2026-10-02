# 差分 ZIP をまとめて 1 つにする（本人の要望、2026-10-02「No.2 を取り込んでいないので 2 と 3 を合わせて」）。
# 取り込んでいない差分が複数あるとき、指定した版（base）から今の全部入りまでの差分を 1 つの ZIP にする。番号は進めない（いまの版のまま）。
#   python tools/crop/make_diff_since.py 1   → No.2〜いままでを合わせた差分 ZIP（info.json は base=1・seq=いまの番号）
# 先に merge.py と make_diff.py を実行して、いまの全部入りの ZIP と記録（snapshot）をそろえておく
import json, os, sys, time, zipfile
import make_diff as M   # 取り込むと make_diff が 1 回走る（変わっていなければ何も作らない）

base = int(sys.argv[1])
prev = json.load(open(M.HIST + f"snapshot-{base:04d}.json", encoding="utf-8"))
cur = M.snapshots()[-1]
with zipfile.ZipFile(M.FULL) as src:
    entries = [e for e in json.loads(src.read("manifest.json")) if prev.get(M.key(e)) != M.now[M.key(e)]]
    dp = M.OUT + f"pocamaster-差分-No{base + 1}-{cur}-{time.strftime('%Y%m%d')}.zip"
    with zipfile.ZipFile(dp, "w", zipfile.ZIP_STORED) as z:
        for e in entries:
            for f in (e["file"], e.get("thumb")):
                if f:
                    z.writestr(f, src.read(f))
        z.writestr("manifest.json", json.dumps(entries, ensure_ascii=False))
        z.writestr("info.json", json.dumps({"kind": "diff", "seq": cur, "base": base, "date": time.strftime("%Y-%m-%d"), "count": len(entries)}))
print(f"No.{base + 1}〜No.{cur} を合わせた差分 ZIP：{len(entries)} 枚 → {dp}（{os.path.getsize(dp) // 1024} KB）")
