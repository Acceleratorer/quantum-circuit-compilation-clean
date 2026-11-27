"""Price the two-product split of the true Wronskian after a quadratic endpoint change."""
import argparse
from collections import Counter
from pathlib import Path
import json,random,sys,time
import numpy as np
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
from paired_jets import F,M,v,extract,physical_errors,WEIGHTS
from projected_derivative import kap,tensors

def plus(x,y):return x[0]^y[0],x[1]^y[1]
def cj(x):return x[0]^x[1],x[1]
def sc(x,a):return F.scale(x,a)
def tr(x):
    y=x
    for _ in range(11):x=M.mul(x,x);y^=x
    return y

def charts(rng,nodes,budget):
    log=np.asarray(M.LOG,dtype=np.int32)
    exp=np.asarray([M.EXP[i%4095]for i in range(8191)],dtype=np.int64)
    def mul(a,b):return np.where((a!=0)&(b!=0),exp[log[a]+log[b]],0)
    def inv(a):return np.where(a!=0,exp[4095-log[a]],0)
    traces=np.array([tr(i)for i in range(4096)],dtype=np.uint8)
    records={}
    for a in nodes:
        klist=np.array([F.sqrt(kap(a)^kap(j))for j in range(a)],dtype=np.int64)
        beta=[0,*[M.inv(int(s))for s in klist]]
        # Normalize every pencil by its public sqrt(k). After a shared terminal
        # potential its determinant on a head z=x+theta*y is A*x^2+B*x*y+C*y^2.
        best=None
        for st in range(0,budget,16384):
            count=min(16384,budget-st)
            u,w,s=rng.integers(0,4096,(3,count))
            landed=[];rs=[]
            for b in beta:
                t=u^b;n=mul(t,t)^mul(t,w)^mul(2048,mul(w,w))
                cross=n^1^s;xx=cross^w;yy=mul(2048,cross)^t^mul(2049,w)
                distinct=(cross!=0)&(traces[mul(mul(xx,yy),mul(inv(cross),inv(cross)))]==0)
                ident=(xx==0)&(yy==0)&(cross==0)
                # c'=0 makes the pencil a real-linear head transform followed by K multiplication.
                lowrank=(s==0)&(n==1)
                landed.append(distinct|ident|lowrank)
            # The A half occurs for old nodes 1..a-1, and each B half occurs once.
            scores=(a-1)*landed[0].astype(int)+np.sum(landed[1:],axis=0);j=int(np.argmax(scores))
            item=(int(scores[j]),int(u[j]),int(w[j]),int(s[j]),[bool(q[j])for q in landed])
            if best is None or item[0]>best[0]:best=item
            if best[0]==2*a-1:break
        total,u,w,s,splits=best
        # A real c' realizes any selected norm, since its norm is c'^2.
        records[a]=dict(u=u,w=w,s=s,d=(F.sqrt(s),0),c=(1^u,w),split=splits,low_rank_steps=total,steps=2*a-1)
    return records

def physical(r,law,shots,records):
    ct=Counter()
    for it in range(shots):
        wt=35 if law=='top'else 19+it%17 if law=='grade'else 31+it%5 if law=='heavy'else r.choices(range(19,36),WEIGHTS)[0]
        err=physical_errors(r,wt,'weighted',it);_,Y,_,_=v.data8(M.syndromes(err))
        try:hs,flags,end,tape=extract(F,[Y[j]for j in range(17)])
        except ZeroDivisionError:ct['source_dropout']+=1;continue
        for a,sol in records.items():
            g=lambda nd:plus(F.kmul(sol['c'],nd),F.kmul(sol['d'],cj(nd)))
            potential=lambda n,d:g(F.ksqrt(F.kmul(n,d)))
            y,dy=Y[a];unit=tape[a-1][0]
            n,d=F.kmul(y,unit),unit
            raw_e=plus(sc(F.ksqrt(dy),F.sqrt(kap(a)^kap(0))),F.ksqrt(y));e=F.kmul(raw_e,unit)
            hnew=plus(e,sc(potential(n,d),F.sqrt(kap(a)^kap(0))))
            for j in range(a):
                k=kap(a)^kap(j);sk=F.sqrt(k)
                for typ,head in ([('A',hs[2*j-1]),('B',hs[2*j])]if j else [('B',hs[0])]):
                    h=F.at(head,a);z=F.ksqrt(h);tz=plus(z,cj(z));mn=tz if typ=='A'else plus(z,sc(tz,sk))
                    e=plus(e,F.kmul(mn,n));prod=F.kmul(z,n)
                    residual=plus(F.kmul(mn,n),g(prod)if typ=='A'else sc(g(prod),sk));hnew=plus(hnew,residual)
                    n,d=sc(plus(d,F.kmul(h,n)),M.inv(k)),n
                    if typ=='B':e=sc(e,M.inv(k));hnew=sc(hnew,M.inv(k))
                    expected=plus(e,sc(potential(n,d),sk if typ=='A' else 1))
                    assert hnew==expected
                    ct['original_half_step_identity']+=1
            den=d if flags.get(2*a-1,False) else n
            sec=F.at(hs[2*a],a)
            if den!=(0,0) and sec!=(0,0):
                output=plus(F.kmul(e,F.kinv(den)),(F.sqrt(hs[2*a-1][1]),0))
                assert F.kmul(output,F.ksqrt(sec))==(1,0)
                ct['checked_actual_second_head']+=1
        ct['originals']+=1
    return ct
def main(o):
    at=time.monotonic();nodes=[int(s)for s in o.nodes.split(',')]
    rec=charts(np.random.default_rng(o.seed),nodes,o.budget);ct=physical(random.Random(o.seed),o.law,o.shots,rec)
    ja,jb=tensors()
    for a,s in rec.items():
        current=(a-1)*len(jb)+sum(len(ja[str(2*(a^j))])for j in range(a))
        s['current_joint']=current;s['separate_after_chart']=(2*a-1)*99+s['low_rank_steps']*84+(2*a-1-s['low_rank_steps'])*99
        s['two_endpoint_products']=198
    result=dict(args=vars(o),charts=rec,counts=ct,seconds=time.monotonic()-at)
    (P/f'wronskian_potential_{o.seed}.json').write_text(json.dumps(result,indent=1)+'\n')
    print(ct,[(a,s['low_rank_steps'],s['steps'],s['current_joint'],s['separate_after_chart'])for a,s in rec.items()])
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('nodes');p.add_argument('law');p.add_argument('shots',type=int);p.add_argument('budget',type=int);p.add_argument('seed',type=int);main(p.parse_args())
