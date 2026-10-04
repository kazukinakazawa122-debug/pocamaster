"""同じ条件で n 回測って、主な項目の中央値を出す（ばらつきが大きいため）。
python tools/perf/bench.py <回数> [環境変数 KEY=VALUE ...]   例: python tools/perf/bench.py 3 CPU=2 NOFILTER=1"""
import json, os, statistics, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
n = int(sys.argv[1]); env = dict(os.environ)
env.setdefault("CPU", "2"); env.setdefault("APP", "http://localhost:4174/pocamaster/")
env.setdefault("PROFILE", "C:/Users/kazuk/AppData/Local/Temp/pocamaster-perf-profile-prof")
for kv in sys.argv[2:]:
    k, v = kv.split("=", 1); env[k] = v
KEYS = ["起動：", "画面：コレクション一覧", "画面：コレクション（IVE SECRET", "スクロール：", "画面：ホーム（戻る）", "画面：設定", "操作：カードを 1 枚タップ", "操作：メンバーを切り替え（ユジン）", "操作：ホームでメンバーを切り替え（すべて）", "操作：検索に「KM」"]
runs = []
for i in range(n):
    out = subprocess.run(["node", "tools/perf/cdp.mjs", "measure"], env=env, capture_output=True, text=True, encoding="utf-8").stdout
    runs.append({r["label"]: r for r in json.loads(out)["結果"]})
def pick(label_prefix):
    return [r for lab, r in ((l, run[l]) for run in runs for l in run if l.startswith(label_prefix))]
for k in KEYS:
    rs = pick(k)
    if not rs: continue
    if "frames" in rs[0]:
        print(f"{k:<34} 描画の間隔の平均 {statistics.median(r['平均_ms'] for r in rs):.0f}ms／遅い描画の割合 {statistics.median(r['遅い描画_33ms超']/r['frames'] for r in rs)*100:.0f}%／最大 {statistics.median(r['最大_ms'] for r in rs):.0f}ms（{n} 回の中央値）")
    else:
        g = lambda r: r.get("画面に出るまで_ms", r.get("内容が出る_ms", 0))
        print(f"{k:<34} 出る {statistics.median(g(r) for r in rs):.0f}ms／落ち着く {statistics.median(r.get('落ち着くまで_ms',0) for r in rs):.0f}ms／処理合計 {statistics.median(r.get('合計_ms',0) for r in rs):.0f}ms")
