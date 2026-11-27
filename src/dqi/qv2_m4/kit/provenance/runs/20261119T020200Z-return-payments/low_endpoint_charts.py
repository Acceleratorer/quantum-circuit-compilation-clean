"""Restrict the norm-one change of Wronskian coordinates to a one-real-word endpoint image."""
import numpy as np,json,time
from aligned_wronskian import P,F,M,kap,plus,cj,tr
from functools import cache
from wronskian_potential import tensors
O=(1,0)
def census():
    log=np.array(M.LOG);exp=np.array([M.EXP[i%4095]for i in range(8191)])
    def mul(a,b):return np.where((a!=0)&(b!=0),exp[log[a]+log[b]],0)
    def inv(a):return np.where(a!=0,exp[4095-log[a]],0)
    trc=np.array([tr(i)for i in range(4096)])
    z=[F.kmul((i,1),F.kinv(cj((i,1))))for i in range(4096)]+[O];assert len(set(z))==4097
    u=np.array([x^1 for x,y in z]);w=np.array([y for x,y in z]);data={}
    for a in range(1,17):
        betas=[0,*[M.inv(F.sqrt(kap(j)^kap(a)))for j in range(a)]]
        split=[]
        for bj in betas:
            t=u^bj;n=mul(t,t)^mul(t,w)^mul(2048,mul(w,w))
            xx=n^w;yy=mul(2048,n)^t^mul(2049,w)
            split.append((n!=0)&(trc[mul(mul(xx,yy),mul(inv(n),inv(n)))]==0))
        scores=(a-1)*split[0]+np.sum(split[1:],axis=0)
        ix=int(np.argmax(scores));s=split
        data[a]=dict(c=z[ix],t=(int(u[ix]),int(w[ix])),weighted_splits=int(scores[ix]),steps=2*a-1,unsplit=[j-1 for j,x in enumerate(s)if not x[ix]],fully_split=int(np.sum(scores==2*a-1)))
    print([(a,x['weighted_splits'],x['steps'],x['fully_split'])for a,x in data.items()])
    (P/'low_endpoint_charts.json').write_text(json.dumps(data,indent=1)+'\n')
if __name__=='__main__':census()
