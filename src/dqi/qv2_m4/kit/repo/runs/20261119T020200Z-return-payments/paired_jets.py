"""Learn exact local ratio and branch availability on the paid original 33 synthesis heads."""
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path
import json,os,random,sys,time
P=Path(__file__).resolve().parent
for d in ('20261118T033800Z-dqi-block-source','20261117T214100Z-dqi-direct-bezout','20261117T184500Z-dqi-source-gauss'):sys.path.append(str(P.parent/d))
from pencil_scale_carrier import F,M,v,physical_errors,extract,tails,WEIGHTS
Z=(0,0)
def deriv(p):return [x if k%2 else 0 for k,x in enumerate(p)if k]
def main():
 p=ArgumentParser();p.add_argument('law',choices=['full','all','axis','weighted']);p.add_argument('count',type=int);p.add_argument('seed',type=int);o=p.parse_args();r=random.Random(o.seed);ct=Counter();at=time.monotonic();samples=[]
 for j in range(o.count):
  w=35 if o.law=='full' else 19+j%17 if o.law in ('all','axis') else r.choices(range(19,36),WEIGHTS)[0]
  e=physical_errors(r,w,o.law,j);sy=M.syndromes(e);_,Y,g,ii=v.data8(sy)
  try:h,flags,carry,tape=extract(F,[Y[i]for i in range(17)])
  except ZeroDivisionError:ct['source_dropout']+=1;continue
  a=v.pass_e(h,g[0],1,v.e_init(1,*g,True),True);b=v.pass_e(h,ii[0],1,v.e_init(1,*ii,False),False)
  ns,ds,fl,extra,_=v.end_block(a,b);v._true_P33[0]=extra
  tr=tails(h,ns,ds);tr[33]=(ns,ds)
  if not v.native_return(h,ns,ds,fl).startswith('ret_ok'):ct['original_source_failure']+=1;continue
  ct['original_rows']+=1
  for i in range(1,17):
   t=2*i-1;x=M.alpha(i);nx,xx=tr[t];n,d=tr[t+1];nr,dr=tr[t+2]
   ev=lambda p:M.pevalK(p,x)
   x0,d0=ev(xx),ev(d);assert ev(nx)==d0
   x1,d1=ev(deriv(xx)),ev(deriv(d));r0=ev(n)
   if d0==Z or r0==Z:ct['paired_zero_denominator']+=1;continue
   iv=F.kinv(d0);pa=F.kmul(x0,iv);pb=F.kmul(d0,F.kinv(r0))
   assert pa==F.at(h[t],i) and pb==F.at(h[t+1],i)
   du=tuple(y^z for y,z in zip(x1,F.kmul(pa,d1)));db=F.kmul(du,iv)
   alt=F.kinv((db[0]^h[t][1],db[1]))
   assert alt==pb
   prior,nxt,_=tape[i-1];q=F.kmul(nxt,F.kinv(prior));ct['joint_quotient_and_jet_exact']+=1
   for k,val in [('d0',d0),('r0',r0),('x0',x0),('d_x',F.kmul(d0,F.kinv(ev(tr[0][1])))if ev(tr[0][1])!=Z else Z),('r_x',F.kmul(r0,F.kinv(ev(tr[0][1])))if ev(tr[0][1])!=Z else Z),('p_a',pa),('p_b',pb)]:
    if val==q:ct['source_unit_ratio_equals_'+k]+=1
   if len(samples)<40:samples.append(dict(slot=t,actual_head=list(pa),second=list(pb),value=list(x0),first_divisor=list(d0),derivative_value=list(x1),derivative_divisor=list(d1),second_divisor=list(r0),previous_unit=prior,next_unit=nxt))
 out=dict(args=vars(o),counts=ct,samples=samples,pid=os.getpid(),affinity=list(os.sched_getaffinity(0)),seconds=time.monotonic()-at);(P/f'paired_jets_{o.seed}.json').write_text(json.dumps(out,indent=1)+'\n');print(json.dumps(ct),flush=True)
if __name__=='__main__':main()
