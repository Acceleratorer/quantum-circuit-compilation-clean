"""Finite trace-one generator bases for the actual joint GF24 product."""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import resource
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
PUBLIC=ROOT/'tools/prize_rebuild_v36/dqi_bundle/tree/q18_source'
HELPER=ROOT/'src/dqi_public_q9_review/gf16_alignment_gate.py'


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load():
    source=HELPER.read_text()
    old="PUBLIC = ROOT/'runs/20261031T040500Z-public-metadata-root/source/somejoint__quantum-circuits-23-17-local-gm-889-qubit-dqi/extracted/blocks/dqi/pro-q8q9-889/source'"
    assert source.count(old)==1
    source=source.replace(old,"PUBLIC = ROOT/'tools/prize_rebuild_v36/dqi_bundle/tree/q18_source'")
    env={'__file__':str(HELPER),'__name__':'joint_basis_reviewed_helper'}
    exec(compile(source,str(HELPER),'exec'),env)
    return env


def bases(h):
    f=h['f']; ar=h['ar']; cols=h['cols']
    sub12=[ar.apply(cols,v) for v in range(4096)]
    sub16=[v for v in sub12 if f.pow(v,16)==v]
    assert len(sub16)==16
    theta=f.primitive_element
    theta=f.mul(theta,f.invert(theta^f.pow(theta,4096)))
    assert theta^f.pow(theta,4096)==1
    translation={min((theta^v)^s for s in sub16) for v in sub12}
    assert len(translation)==256
    result=set()
    for t in translation:
        orbit=[min(f.pow(t,16**i)^s for s in sub16) for i in range(3)]
        assert all(v in translation for v in orbit)
        if f.pow(t,256)==t:
            continue  # The one degree2 class cannot supply a degree6 basis.
        # Frobenius also transforms c. Keep all three representatives because
        # the actual fixed c set is not assumed closed under that action.
        result.add(t)
    assert len(result)==255
    return sorted(result)


def evaluations(h,theta):
    f,sub,ar=h['f'],h['sub'],h['ar']
    embed,_=h['evaluations']()
    basis=[f.mul(v,f.pow(theta,j)) for j in range(6) for v in embed]
    inv=ar.inverse_columns(basis)
    evs=[]
    for point in list(range(16))+[None]:
        values=[]
        for co in inv:
            v=(co>>20)&15 if point is None else 0
            if point is not None:
                for j in reversed(range(6)):v=sub.mul(v,point)^((co>>(4*j))&15)
            values.append(v)
        evs.append(values)
    return evs


def representatives(h,evs):
    f,ar=h['f'],h['ar']
    dual=[sum(h['trace'](f.mul(1<<i,1<<j))<<i for i in range(24)) for j in range(24)]
    inverse=ar.inverse_columns(dual)
    # Tensor4 first mask is fixed across every evaluation, ensuring one dual convention.
    first=h['kernels'].tensor4()[0][0]
    return [ar.apply(inverse,h['pull'](first,ev)) for ev in evs]


def align(h,c,aa):
    f,ar=h['f'],h['ar']; cp=ar.apply(h['cols'],c)
    bb=[f.mul(cp^1,a)^f.pow(a,4096) for a in aa]
    dd=[f.pow(a,1<<23) for a in aa]
    assert all(bb)
    ainv=[f.invert(f.pow(a,15)) for a in aa]
    bk=[f.pow(v,15) for v in bb]; dk=[f.pow(v,15) for v in dd]
    groups=defaultdict(list)
    for i in range(len(aa)):
        for j in range(len(aa)):
            groups[f.mul(bk[j],ainv[i]),f.mul(dk[j],ainv[i])].append((i,j))
    matches=max(groups.values(),key=lambda x:(len(x),tuple(x)))
    assert len(set(i for i,j in matches))==len(set(j for i,j in matches))==len(matches)
    i,j=matches[0]
    return dict(c=c,matches=matches,blocks=len(matches),
                lam=f.mul(bb[j],f.invert(aa[i])),mu=f.mul(dd[j],f.invert(aa[i])))


def scout(h,run,plan):
    # Reuse the earlier exact field/PAIR4/corruption controls on current source files.
    oldev,tensor,aa=h['setup']()
    counts=h['contexts'](); assert sum(counts.values())==216
    oldrows=[align(h,c,aa) for c in counts]
    assert max(r['blocks'] for r in oldrows)==1
    oldall=representatives(h,evaluations(h,h['f'].primitive_element))
    assert all(align(h,c,oldall)['blocks']==1 for c in counts)
    winners={c:dict(c=c,blocks=1,theta=None) for c in counts}; histogram=Counter(); theta_list=bases(h)
    for index,theta in enumerate(theta_list):
        evs=evaluations(h,theta); aa=representatives(h,evs)
        for c in counts:
            row=align(h,c,aa); row['theta']=theta; histogram[row['blocks']]+=1
            if row['blocks']>winners[c]['blocks']:winners[c]=row
        (run/'progress.json').write_text(json.dumps(dict(bases_done=index+1,total_bases=len(theta_list),
            best_saving_T=sum(6*(r['blocks']-1)*counts[c] for c,r in winners.items())))+'\n')
    saving=sum(6*(r['blocks']-1)*counts[c] for c,r in winners.items())
    assert 216*192+198*182==plan['actual_joint_unconditional_T']==77508
    return dict(status='PASS_FINITE_TRACE_ONE_BASIS_GATE',evidence='diagnostic',bases=theta_list,
        contexts=dict(counts),winners=list(winners.values()),block_histogram=dict(histogram),
        projected_saving_T=saving,qualifies=saving>=plan['min_saving_T'],
        actual_source_bill=77508,old_basis_max_blocks=1,
        scope='All255 degree6 trace-one generators modulo GF16 translations, all17 evaluation points, actual31 nonzero-c constants. Frobenius is not quotiented because it also transforms c. Scalar isotopies only; no claim about other general tensors or non-trace-one generator families.')


def tensor(h,evs,points):
    masks=[h['pull'](m,evs[i]) for i in points for m,v in h['kernels'].tensor4()]
    f=h['f']; equations=[]
    for i in range(24):
        for j in range(i,24):
            equations.append((sum(((m>>i)&(m>>j)&1)<<k for k,m in enumerate(masks)),f.mul(1<<i,1<<j)))
    vv=h['ar']._solve_output_vectors(equations,len(masks))
    assert len(masks)==99 and all(vv)
    return list(zip(masks,vv))


def construct(h,row):
    f,ar=h['f'],h['ar']; evs=evaluations(h,row['theta'])
    lc=[f.mul(row['lam'],1<<i) for i in range(24)];mc=[f.mul(row['mu'],1<<i) for i in range(24)]
    cp=ar.apply(h['cols'],row['c'])
    hc=[f.mul(cp^1,1<<i)^f.pow(1<<i,4096) for i in range(24)]
    sq=[f.square(1<<i) for i in range(24)]
    left={i for i,j in row['matches']};right={j for i,j in row['matches']}
    lp=sorted(left)+[i for i in range(17) if i not in left][:11-len(left)]
    rp=sorted(right)+[i for i in range(17) if i not in right][:11-len(right)]
    lt,rt=tensor(h,evs,lp),tensor(h,evs,rp);forms=[]
    for i,j in row['matches']:
        x=[ar.apply(evs[j],v) for v in hc]
        y=[h['sub'].pow(ar.apply(evs[j],v),8) for v in sq]
        forms += [(h['pull'](a,x),h['pull'](b,y)) for a,b,w in h['xs']['PAIR4']]
    for points,terms,matched,l,r in ((lp,lt,left,lc,mc),(rp,rt,right,hc,sq)):
        for k,i in enumerate(points):
            if i not in matched:forms += [(h['pull'](m,l),h['pull'](m,r)) for m,w in terms[9*k:9*k+9]]
    expected=h['target'](row['c']);eq=[]
    for i in range(24):
        for j in range(24):
            eq.append((sum((((a>>i)&1)*((b>>j)&1))<<k for k,(a,b) in enumerate(forms)),expected[24*i+j]))
    vectors=ar._solve_output_vectors(eq,len(forms));result=[(a,b,w) for (a,b),w in zip(forms,vectors) if w]
    assert h['coefficients'](result)==expected and len(result)<=198-6*row['blocks']
    actual=[(h['pull'](a,h['cols']),h['pull'](b,h['cols']),
             ar.apply(h['invcols'],w&((1<<24)-1))|(ar.apply(h['invcols'],w>>24)<<24)) for a,b,w in result]
    assert h['coefficients'](actual)==h['target'](row['c'],True)
    return actual


def followup(h,run,plan,positive):
    s=json.loads((run/'scout.json').read_text());assert s['qualifies']==positive
    if not positive:
        return dict(status='CLOSED_FINITE_TRACE_ONE_BASIS_FAMILY',projected_saving_T=s['projected_saving_T'],
                    scope=s['scope'],decision='No whole build, no new basis seeds or longer search. General multiplication remains a separate representation dependency.')
    tables={}
    for row in s['winners']:
        if row['blocks']>1:tables[row['c']]=construct(h,row)
    (run/'tensors.json').write_text(json.dumps(tables)+'\n')
    return dict(status='PASS_EXACT_BASIS_TENSORS',tables=len(tables),basis_pairs_per_table=576,
                projected_saving_T=s['projected_saving_T'],sha256=sha(run/'tensors.json'),
                next='Native arbitrary dirty-target/phase controls and source-bound whole constructor required before score claim.')


if __name__=='__main__':
    run=Path(sys.argv[1]).resolve();mode=sys.argv[2];plan=json.loads((run/'plan.json').read_text())
    for p,digest in plan['hashes'].items():assert sha(ROOT/p)==digest,p
    start=time.monotonic();h=load()
    result=scout(h,run,plan) if mode=='scout' else followup(h,run,plan,mode=='construct')
    result.update(seconds=time.monotonic()-start,maxrss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    (run/(mode+'.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('winners','bases')}),flush=True)
