"""Build forced-generator padding and the official conditional weight law."""
import hashlib
import json
import random
import sys
from source_maps import HERE,ROOT,M,physical
sys.path.insert(0,str(ROOT/'official/2026-10-27/kickmix'))
sys.path.insert(0,str(ROOT/'official/2026-10-27/verifiers/dqi'))
from verify_submission_dqi import optimal_dqi_weights


def main():
    weights=optimal_dqi_weights(4095,35,12,2016)**2;rng=random.Random(55931);rows=[]
    for i in range(19,36):
        unique=set()
        for j in range(5):
            d=physical(rng,i);assert d is not None
            a,b=d[0],d[1]
            while b:a,b=b,M.pmod(a,b)
            unique.add(tuple(M.pscale(a,M.inv(a[-1]))))
        assert len(unique)==1
        pad=unique.pop();assert len(pad)==36-i
        rows.append(str(i)+' '+str(float(weights[i]))+' '+' '.join(map(str,pad)))
    file=HERE/'physical_locators.dat';file.write_text('\n'.join(rows)+'\n')
    print('Excluded official probability below weight 19',sum(weights[:19]),'source',hashlib.sha256(file.read_bytes()).hexdigest())


if __name__=='__main__':main()
