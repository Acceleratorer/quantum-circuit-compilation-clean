# SPDX-License-Identifier: Apache-2.0
"""Install the native 17-word quotient-chain solve in the production odd-degree converter."""
from functools import lru_cache
import inspect
import json
from pathlib import Path
import sys

HOME_DIR=Path(__file__).resolve().parent


def load_bodies(scope):
    # Component precursors also have standalone true-value and phase entrypoints.
    for file,start,end in (
        ('emit_source.py','@lru_cache(None)\ndef cols','\nstart=time.monotonic();n=args.degree;'),
        ('emit_payload.py','def multi_div','\nstart=time.monotonic();n=args.degree;'),
        ('emit_transpose.py','def h_one','\nstart=time.monotonic();n=args.degree;'),
        ('emit_pairwalk.py','O=V.P.DirectArithmetic','\nstart=time.monotonic();n=args.degree;'),
        ('emit_chain.py','def mul_keep','\ndef whole_truth'),
    ):
        path=HOME_DIR/file;data=path.read_text();lo=data.index(start);hi=data.index(end,lo)
        exec(compile(data[lo:hi],str(path),'exec'),scope)
    scope['MIDDLE']=scope['centre']


def check_lifecycle(module,name,replacements):
    old=getattr(module,name);s=inspect.getsource(old)
    for before,after in replacements:
        if s.count(before)!=1:raise ValueError((module.__name__,name,before,s.count(before)))
        s=s.replace(before,after)
    exec(compile(s,'<quadratic source lifecycle checks>','exec'),module.__dict__)


def install(V,CE,out):
    import kickmix as km
    from tower_inverse import apply_inplace_linear,erase_norm,init_norm,invert_inplace,kernel,phase_product,rows_from_columns,xor_product
    from quantum_reciprocal import xor_linear
    from quadratic import M,Place,deflate,places
    from source_maps import inverse,mv,transpose
    scope=dict(locals());scope.update(lru_cache=lru_cache)
    load_bodies(scope)
    count=[];core=V.NewCore
    def body(builder,A,B,rhss,inverse=True,context=None,closing=False):
        A=list(A);B=list(B);Y=[list(v) for v in rhss]
        assert not (inverse==closing) and len(A)==18 and len(B)==17 and len(Y)==2
        assert context.builder_id==id(builder) and not context.local_flags
        context.gauge_carrier.clean_boundary();entry=builder.num_allocated_qubits
        if closing:
            history=context.outer.pop('quadratic_source_chain')
            scope['walk'](builder,A,B,Y,17,True,history)
        else:
            assert 'quadratic_source_chain' not in context.outer
            context.outer['quadratic_source_chain']=scope['walk'](builder,A,B,Y,17,False,None)
        assert builder.num_allocated_qubits==entry;context.gauge_carrier.clean_boundary()
        count.append(dict(closing=closing,live=entry))
        (out/'chain_hook_calls.json').write_text(json.dumps(count,indent=2)+'\n')
    core.emit=body
    check_lifecycle(V.NewOuter,'emit_prefix',[('assert context.gauge_h_requeries==1','assert context.gauge_h_requeries==0')])
    check_lifecycle(V,'emit',[
        ('assert outer.core.gauge_h_requeries == 1','assert outer.core.gauge_h_requeries == 0'),
        ('assert len(outer.core.local_created) == len(outer.core.local_retired) == 32','assert len(outer.core.local_created) == len(outer.core.local_retired) == 0'),
        ('assert (carrier.parks, carrier.unparks) == (14,14)','assert (carrier.parks, carrier.unparks) == (0,0)'),
        ('assert carrier.parked_phase_payments == 2',"assert getattr(carrier, 'parked_phase_payments', 0) == 0"),
    ])
