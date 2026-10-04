"""直す前（dist-prof-base）と、いま（dist-prof-new）を、同じサーバー（dist-prof を配る preview 4174）で交互に測って比べる。
python tools/perf/ab.py <回数> [KEY=VALUE ...]"""
import json, os, shutil, statistics, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
n = int(sys.argv[1]); env = dict(os.environ)
env.setdefault("CPU", "2"); env.setdefault("APP", "http://localhost:4174/pocamaster/")
env.setdefault("PROFILE", "C:/Users/kazuk/AppData/Local/Temp/pocamaster-perf-profile-prof")
for kv in sys.argv[2:]:
    k, v = kv.split("=", 1); env[k] = v
def use(variant):
    shutil.rmtree("dist-prof", ignore_errors=True); shutil.copytree("dist-prof-" + variant, "dist-prof")
res = {"base": [], "new": []}
for i in range(n):
    for v in ("base", "new"):
        use(v)
        out = subprocess.run(["node", "tools/perf/cdp.mjs", "measure"], env=env, capture_output=True, text=True, encoding="utf-8").stdout
        res[v].append({r["label"]: r for r in json.loads(out)["結果"]})
        print(f"  {v} {i+1}/{n} 済み", flush=True)
json.dump(res, open(os.environ.get("AB_OUT", "ab.json"), "w", encoding="utf-8"), ensure_ascii=False)
labels = [l for l in res["base"][0] if not l.startswith("(準備")]
def med(v, l, f): return statistics.median(f(run[l]) for run in res[v] if l in run)
for l in labels:
    r0 = res["base"][0][l]
    if "frames" in r0:
        f = lambda r: r["平均_ms"]; g = lambda r: r["遅い描画_33ms超"] / r["frames"] * 100
        print(f'{l[:36]:<38} 描画の間隔の平均 {med("base",l,f):.0f}ms → {med("new",l,f):.0f}ms／遅い描画 {med("base",l,g):.0f}% → {med("new",l,g):.0f}%')
    else:
        f = lambda r: r.get("落ち着くまで_ms", 0); g = lambda r: r.get("画面に出るまで_ms", r.get("内容が出る_ms", 0))
        print(f'{l[:36]:<38} 出る {med("base",l,g):.0f} → {med("new",l,g):.0f}ms／落ち着く {med("base",l,f):.0f} → {med("new",l,f):.0f}ms')
