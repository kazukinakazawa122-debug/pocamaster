"""albums_ida_check.py のラベルの確かめ（2026-09-30）

ラベルを付けた 1 人のカードごとに、ほかのメンバーの表の同じ位置のカードが、アプリのどの枠の画像と同じ写真か（似ている度合い 0.8 以上）を調べる。
2 人以上が同じ別の枠を指し、ラベルの枠を指す人がいないときに表示する（ラベルのまちがいの候補）。
使い方：python audit_ida.py 結果.json gaeul,rei   （2 つめは調べる表。TABLES のキーをカンマで）
"""
import json,glob,sys
from collections import Counter
import numpy as np
from PIL import Image
from build2 import *
import grid
from hires_ida import feat
from albums_ida_check import TABLES, D, X
KEYS=[("yujin","ユジン"),("gaeul","ガウル"),("rei","レイ"),("wonyoung","ウォニョン"),("liz","リズ"),("leeseo","イソ")]
cur={}
for p in sorted(glob.glob(SP+"out/*.json")):
    if 'zzzz' in p: continue
    for e in json.load(open(p,encoding="utf-8"))["images"]:
        if len(e["members"])==1: cur[(e["collection"],e["members"][0],e["source"],e["version"])]=e["file"]
FE={}
for k,n in KEYS:
    sl=[(kk,f) for kk,f in cur.items() if kk[1]==n]
    FE[k]=(sl,np.array([feat(Image.open(CARDS+f)) for kk,f in sl]))
pages={}
def pg(k,p):
    if (k,p) not in pages:
        im=grid.load(D+f"{k}_{p}.jpg"); pages[(k,p)]=(im,grid.card_boxes(im,min_w=0.03,max_w=0.08))
    return pages[(k,p)]
res=[]
for key,(name,table) in [(k,v) for k,v in TABLES.items() if k in sys.argv[2].split(",")]:
    miss=json.load(open(SP+f"review/miss_{key}.json"))
    for i,(c,s,v,kind) in sorted(table.items()):
        if kind==X: continue
        p,b,_=miss[i]; cx,cy=(b[0]+b[2])/2,(b[1]+b[3])/2
        votes=[]
        for k,n in KEYS:
            if k==key: continue
            im,bs=pg(k,p); bx=min(bs,key=lambda x:abs((x[0]+x[2])/2-cx)+abs((x[1]+x[3])/2-cy))
            sl,F=FE[k]; sc=F@feat(im.crop(inset_frame(im,bx))); j=int(sc.argmax())
            if sc[j]>=0.8: votes.append((sl[j][0][0],sl[j][0][2],sl[j][0][3]))
        cnt=Counter(votes)
        if not cnt: continue
        top,nv=cnt.most_common(1)[0]
        if top!=(c,s,v) and nv>=2 and (c,s,v) not in cnt:
            res.append([key,i,c,s,v,kind,top[0],top[1],top[2],nv,len(votes)])
            print(key,i,(c,s,v,kind),"→",top,f"{nv}/{len(votes)}",flush=True)
json.dump(res,open(sys.argv[1],"w",encoding="utf-8"),ensure_ascii=False)
