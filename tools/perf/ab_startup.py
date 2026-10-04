"""2 回目以降の起動を、直す前（dist-prof-base）と今（dist-prof-new）で交互に測る。python tools/perf/ab_startup.py <交互の回数>"""
import json, os, shutil, statistics, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
n = int(sys.argv[1]); env = dict(os.environ)
env.setdefault("CPU", "2"); env.setdefault("APP", "http://localhost:4174/pocamaster/"); env.setdefault("K", "3")
env.setdefault("PROFILE", "C:/Users/kazuk/AppData/Local/Temp/pocamaster-perf-profile-prof")
res = {"base": [], "new": []}
for i in range(n):
    for v in ("base", "new"):
        shutil.rmtree("dist-prof", ignore_errors=True); shutil.copytree("dist-prof-" + v, "dist-prof")
        out = subprocess.run(["node", "tools/perf/cdp.mjs", "startup"], env=env, capture_output=True, text=True, encoding="utf-8").stdout
        res[v] += json.loads(out)
        print(f"  {v} {i+1}/{n}", flush=True)
for key in ("内容が出る_ms", "落ち着く_ms", "処理合計_ms", "最長_ms"):
    print(f"{key:<14} 前 {statistics.median(r[key] for r in res['base']):.0f} → 後 {statistics.median(r[key] for r in res['new']):.0f}  （前 {[r[key] for r in res['base']]}／後 {[r[key] for r in res['new']]}）")
