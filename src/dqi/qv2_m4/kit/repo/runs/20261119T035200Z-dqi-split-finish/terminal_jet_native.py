"""Fuse the derivative in the original eight irreducible terminal factors."""
from pathlib import Path
import inspect
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from split_finish import make_scope,BLOCK
from terminal_jet_tensor import geometry

def prefix(f,b,sw,aw,uw,vw):
    from field_tensor import accumulate_product
    from quantum_reciprocal import xor_linear
    terms,cols,_,_=geometry();km=f['km'];arithmetic=f['O'].A
    temp=b.alloc_qubits(24)
    left=km.array([*sw,*aw]);right=km.array([*uw,*vw])
    accumulate_product(b,left,right,temp,terms)
    b.swap(vw,temp)
    mask=b.alloc_bits(24);b.hmr(temp,mask);b.free(temp)
    rec_v=arithmetic.make_record(b,mask)
    rec_u=arithmetic.emit_prefix(b,sw,uw,2048)
    xor_linear(b,uw,vw,cols)
    return rec_v,rec_u

def install_scope(f,negative=False):
    def emit(b,sw,aw,uw,vw):
        return prefix(f,b,sw,aw,uw,vw)
    f['jet_prefix']=emit
    source=(BLOCK/'emit_finish_member.py').read_text()
    raw=source[source.index('def final_cells'):source.index('\ndef finish_map')]
    old='recV=O.A.emit_prefix(b,sw,vw,2048);O.A.product(b,aw,uw,vw,2048)\n            recU=O.A.emit_prefix(b,sw,uw,2048);created[i]=(recV,recU)'
    assert raw.count(old)==1
    raw=raw.replace(old,'created[i]=jet_prefix(b,sw,aw,uw,vw)')
    # The held member pays the two real inverse-norm masks together.
    old='du=multi_div(b,sw,[uw]);pay_division(b,sw,[uw],du);'
    assert raw.count(old)==1
    raw=raw.replace(old,'du=multi_div(b,sw,[uw]);')
    old='dv=multi_div(b,sw,[vw]);pay_division(b,sw,[vw],dv);'
    assert raw.count(old)==1
    raw=raw.replace(old,'dv=multi_div(b,sw,[vw]);b.cx(dv[0].inverse_norm_mask,du[0].inverse_norm_mask);b.free(dv[0].inverse_norm_mask);dv[0].inverse_norm_mask=None;pay_division(b,sw,[uw,vw],du+dv);')
    if negative:
        old="O.A.repay_product_input(b,vw,recs[i][0])"
        assert raw.count(old)==1
        raw=raw.replace(old,"(O.A.free_product_mask(b,recs[i][0]) if i==0 else O.A.repay_product_input(b,vw,recs[i][0]))")
    exec(compile(raw,'<native Hermite terminal>', 'exec'),f)
    return f['finish_map'],f['square'](f['factors'](0,8))

def build(v,ce,out,offset=0,slots=0,negative=False):
    return install_scope(make_scope(v,ce,out),negative)

def patch_incumbent():
    import fusion_hook
    fusion_hook.make_finish_map=lambda v:install_scope(fusion_hook.arithmetic_scope(v))

def closing(f,b,sw,aw,uw,vw,records):
    arithmetic=f['O'].A
    du=f['multi_div'](b,sw,[uw])
    arithmetic.repay_product_input(b,uw,records[1])
    arithmetic.product(b,aw,uw,vw,2048)
    dv=f['multi_div'](b,sw,[vw])
    b.cx(dv[0].inverse_norm_mask,du[0].inverse_norm_mask)
    b.free(dv[0].inverse_norm_mask)
    dv[0].inverse_norm_mask=None
    f['pay_division'](b,sw,[uw,vw],du+dv)
    arithmetic.repay_product_input(b,vw,records[0])

def main():
    import emit
    neg='--unpaid' in sys.argv
    if neg:sys.argv.remove('--unpaid')
    env=dict(vars(emit),build=lambda v,ce,out,offset,slots:build(v,ce,out,offset,slots,neg))
    exec(compile(inspect.getsource(emit.main),'<original Hermite converter>','exec'),env);env['main']()
if __name__=='__main__':main()
