import json, sys
sys.stdout.reconfigure(encoding="utf-8")
def load(p): return {r["label"]: r for r in json.load(open(p, encoding="utf-8"))["結果"]}
a = load(sys.argv[1]); b = load(sys.argv[2]) if len(sys.argv) > 2 else None
def fmt(r):
    if r is None: return "-"
    if "frames" in r: return f'遅い描画 {r["遅い描画_33ms超"]}/{r["frames"]}（最大 {r["最大_ms"]}ms）'
    return f'出る {r.get("画面に出るまで_ms", r.get("内容が出る_ms","-"))}ms／落ち着く {r.get("落ち着くまで_ms","-")}ms／処理合計 {r.get("合計_ms","-")}ms'
for k, r in a.items():
    if k.startswith("(準備"): continue
    print(f"{k[:34]:<36} 前: {fmt(r)}")
    if b: print(f"{'':<36} 後: {fmt(b.get(k))}")
