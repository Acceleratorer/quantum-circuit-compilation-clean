# SPDX-License-Identifier: Apache-2.0
"""Install a single odd-degree source-to-scan map in the existing complete DQI decoder."""
from functools import lru_cache
import inspect
import json
from pathlib import Path
from chain_hook import load_bodies


def arithmetic_scope(V):
    """Load the native field, polynomial and shared-reciprocal operations."""
    import kickmix as km
    import confluent_ext as CE
    from tower_inverse import apply_inplace_linear,erase_norm,init_norm,invert_inplace,kernel,phase_product,rows_from_columns,xor_product
    from quantum_reciprocal import xor_linear
    from quadratic import M,Place,deflate,places,pad
    from source_maps import inverse,mv,transpose
    from compact_finish import factors,kmul,basis,point_l
    from finish_fusion import square
    scope=dict(locals());scope.update(lru_cache=lru_cache);load_bodies(scope)
    for file,lo,hi in [('emit_fusion.py','def qi_component','\ndef fused_truth'),('emit_finish_member.py','@lru_cache(None)\ndef hroot','\ndef real_reference')]:
        path=Path(__file__).resolve().with_name(file);data=path.read_text();a=data.index(lo);b=data.index(hi,a);exec(compile(data[a:b],str(path),'exec'),scope)
    return scope


def make_finish_map(V):
    """Return (in-place D,p -> D,K circuit, public P^2 coefficients)."""
    scope=arithmetic_scope(V)
    return scope['finish_map'],scope['square'](scope['factors'](0,8))


def configure_scan(V,Mpub,source_multiplier=None):
    """Install the scan whose public divisor at x is x*source_multiplier(x)*P²(x)."""
    adaptive=V.Adaptive
    if not hasattr(adaptive,'direct_finish_original_scan'):
        adaptive.direct_finish_original_scan=adaptive.emit_scan
    raw=inspect.getsource(adaptive.direct_finish_original_scan)
    old="OriginalScan.Finish.geometry()['M']";assert raw.count(old)==1
    V.Adaptive.quadratic_finish_public=Mpub
    raw=raw.replace(old,'quadratic_finish_public')
    if source_multiplier is not None:
        old="OriginalScan.geometry()['U']";assert raw.count(old)==1
        adaptive.direct_finish_source_multiplier=list(source_multiplier)
        raw=raw.replace(old,'direct_finish_source_multiplier')
    exec(compile(raw,'<direct numerator public mask multiplier>','exec'),adaptive.__dict__)
    return adaptive.emit_scan


def install(V,CE,out):
    run,Mpub=make_finish_map(V)
    configure_scan(V,Mpub)
    def complete(builder,syndromes,masks,*,j_min=15,scan_positions=4095,stage=lambda _:None):
        V.assert_bindings();assert j_min==15 and scan_positions==4095 and len(syndromes)==70 and len(masks)==4095
        gauge=V.Adaptive.open_gauge(builder,list(syndromes),masks,stage=stage);assert not gauge.closed and gauge.scans==0
        key=V.emit_key_prefix(builder,syndromes,j_min=j_min,stage=stage);D,N=key['D'],key['N'];entry=builder.num_allocated_qubits
        data=run(builder,D,N);assert builder.num_allocated_qubits==entry
        scan=V.Adaptive.emit_scan(builder,D,N,masks,gauge,positions=scan_positions,stage=stage);assert scan['point_tests']==4026 and scan['full_cycle'] and gauge.scans==1
        run(builder,D,N,True,data);assert builder.num_allocated_qubits==entry
        V.emit_key_closing(builder,key,stage=stage);closure=V.Adaptive.close_gauge(builder,masks,gauge,stage=stage)
        assert gauge.closed and gauge.scans==1 and closure['all_owned_classical_bits_retired_zero'] and builder.num_allocated_qubits==840
        (out/'scan_fusion_calls.json').write_text(json.dumps(dict(physical_words=[len(D),len(N)],live_qubits=entry,scan_tests=scan['point_tests'],source_scan_restored=True,M=Mpub),indent=2)+'\n')
        return dict(source_to_scan='packed_quadratic_residues',scan=scan)
    V.emit=complete
