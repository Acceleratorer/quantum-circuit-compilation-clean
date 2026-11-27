# SPDX-License-Identifier: Apache-2.0
"""Runs INSIDE tools/dqi_pair/sandbox.py. Builds Syed Asad Ali's v12 DQI decoder (Apache-2.0) with the confluent extractor
of confluent_ext.py installed, in one of these modes, and writes OUT/MODE.kmx (or .kmb) plus OUT/wires.json:
  ext    syndrome geometry + confluent extractor prefix (heads left in the words)
  extrt  ext + its closing + inverse geometry (should be the identity on the syndromes)
  key    key prefix (geometry, extractor, gauge, seed, synthesis) + key closing
  full   the whole decoder (v7_pipeline.emit), kmb
  args: --src --official --out MODE"""
import argparse, json, os, shutil, sys, time, zipfile
from pathlib import Path
ap = argparse.ArgumentParser()
ap.add_argument('--src', type=Path); ap.add_argument('--official', type=Path); ap.add_argument('--out', type=Path)
ap.add_argument('mode'); ap.add_argument('--maxq', type=int, default=889)
ap.add_argument('--np', type=int, default=1)
a = ap.parse_args()
CODE = Path(__file__).resolve().parent
T0 = time.time()
BUILD = Path('/tmp/conf_build'); shutil.rmtree(BUILD, ignore_errors=True); BUILD.mkdir()
with zipfile.ZipFile(a.src / 'dqi_source_zip') as z:
    z.extractall(BUILD)
ROOT = BUILD / 'dqi_source' / 'src'
OFF = ROOT / 'pro1_controller_bundle' / '1_task' / 'official'; OFF.mkdir(parents=True, exist_ok=True)
shutil.copy(a.official / 'kickmix' / 'kickmix.so', OFF / 'kickmix.so')
VDIR = ROOT / 'pro1_controller_bundle' / '1_task' / 'verifiers' / 'dqi'; VDIR.mkdir(parents=True, exist_ok=True)
shutil.copy(a.official / 'verifiers' / 'dqi' / 'verify_submission_dqi.py', VDIR / 'verify_submission_dqi.py')
sys.path.insert(0, str(ROOT / 'controller_work' / 'after_v3' / 'integration_v7'))
os.chdir(ROOT)
import v7_pipeline as V7
V7.configure()
sys.path.insert(0, str(CODE))
import confluent_ext as CE
inst = CE.install(V7)
import npclose as NPC   # lane dqi_close v11: norm-preserving closing on unguarded records + case-1 closings
NPC.install(V7.P.Arithmetic, CE, enable=a.np == 1)
if a.mode == 'fullnp':
    import nopark; nopark.apply(); a.mode = 'full'; a.maxq = 890
if a.mode == 'fullnptag':   # lane dqi_rank: fullnp gates + stage INFO_TAG markers
    import nopark; nopark.apply(); a.mode = 'fulltag'; a.maxq = 890
import kickmix as km
b = km.CircuitBuilder(); b.set_max_qubits(a.maxq)
S = [b.create_quantum_register(12, f"S{i}") for i in range(70)]
info = dict(mode=a.mode, S=[[q.id for q in r] for r in S])
NEG = a.mode.endswith('neg')
if NEG: a.mode = a.mode[:-3]
if a.mode == 'extrtneg':
    CE.NEG_DROP = True
    a.mode = 'extrt'
if a.mode == 'extrttag':
    # lane dqi_close: extrt with INFO_TAG markers around the return sub-blocks (no effect on simulation)
    def tagwrap(obj, name, tag):
        f = getattr(obj, name)
        def g(*args, **kw):
            b.info_tag(f'@enter:{tag}'); r = f(*args, **kw); b.info_tag(f'@exit:{tag}'); return r
        setattr(obj, name, g)
    E_ = inst['ext']
    tagwrap(CE, 'restore_multi', 'restore_multi'); tagwrap(E_.A, 'inverse_closed', 'inverse_closed')
    tagwrap(E_.A, 'repay_source_masks', 'repay_src'); tagwrap(E_.Tail, 'zero_phase', 'zero_phase')
    tagwrap(E_.Tail, 'erase_zero_flag', 'erase_zero_flag'); tagwrap(E_, 'old_double', 'old_double')
    tagwrap(E_, 'prev_flag', 'prev_flag'); tagwrap(E_, 'zero', 'zero')
    a.mode = 'extrt'; TAGGED = True
else:
    TAGGED = False
if a.mode == 'prims':
    # lane dqi_v9b: static T and qubits of the end-node primitives (each on a fresh builder)
    from tower_inverse import invert_inplace, xor_product, phase_product, kernel
    from compact_inverse22 import compact_inverse_twelve as ci22
    from phase_inverse12 import phase_inverse_twelve_polynomial as pinv
    Tl = inst['ext'].Tail; res = {}
    def meas(name, f):
        bb = km.CircuitBuilder(); bb.set_max_qubits(200)
        x = bb.alloc_qubits(12); y = bb.alloc_qubits(12); m = bb.alloc_bits(12); bb.bit_store(m, False)
        f(bb, x, y, m); c = bb.finish_circuit()
        res[name] = (c.operation_statistics().num_toffoli_like, c.num_qubits - 24)
    meas('invert_inplace', lambda bb, x, y, m: invert_inplace(bb, x))
    meas('ci22', lambda bb, x, y, m: ci22(bb, x))
    meas('pinv', lambda bb, x, y, m: pinv(bb, x, m))
    meas('xor_product', lambda bb, x, y, m: xor_product(bb, x, y, bb.alloc_qubits(12)))
    meas('phase_product', lambda bb, x, y, m: phase_product(bb, x, y, m, kernel(12)))
    def zx(bb, x, y, m):
        f = bb.alloc_qubits(1)[0]; Tl.zero_xor(bb, x, f)
    meas('zero_xor', zx)
    def zxe(bb, x, y, m):
        f = bb.alloc_qubits(1)[0]; Tl.zero_xor(bb, x, f); Tl.erase_zero_flag(bb, x, f)
    meas('zero_xor+erase', zxe)
    print('PRIMS', json.dumps(res), flush=True); sys.exit(0)
if a.mode in ('e0rt', 'e0fwd'):
    # lane dqi_v9b baseline: extractor (33 heads) + v7 gauge round trip, f31 kept live (cost reference for e1rt)
    ext = inst['ext']; Tail = ext.Tail
    inst['Public'].emit(b, S)
    heads = [km.array([*S[2 * i], *S[2 * i + 1]]) for i in range(33)]
    carry = b.alloc_qubits(24); b.x(carry[0])
    rec = ext.prefix(b, heads, carry)
    gauge = Tail.gauge_prefix(b, carry)
    if a.mode == 'e0rt':
        Tail.gauge_return(b, carry, gauge)
        ext.closing(b, heads, carry, rec)
        b.x(carry[0]); b.free(carry); inst['Public'].emit(b, S, True)
elif a.mode in ('e1fwd', 'e1rt'):
    # lane dqi_v9b: extractor (33 heads) + v7 gauge + sequential end node forward; N, D word ids in wires.json
    import endnode as EN
    ext = inst['ext']; Tail = ext.Tail
    inst['Public'].emit(b, S)
    heads = [km.array([*S[2 * i], *S[2 * i + 1]]) for i in range(33)]
    carry = b.alloc_qubits(24); b.x(carry[0]); info['carry'] = [q.id for q in carry]
    rec = ext.prefix(b, heads, carry)
    mE31 = ext.hmr_flag(rec.pop('E'))
    gauge = Tail.gauge_prefix(b, carry)
    SE = EN.SeqEnd(CE.SLOT_NODE, Tail)
    N, D, R = SE.forward(b, heads, S[66], S[67], S[68], S[69], carry[:12])
    info['N'] = [[q.id for q in w] for w in N]; info['D'] = [[q.id for q in w] for w in D]
    if a.mode == 'e1rt':
        if NEG: b.x(D[1][3])
        (_, lam, _), (Ep, mz) = SE.reverse(b, heads, N, D, R, ext=ext, mE31=mE31)
        assert tuple(lam) == tuple(carry[:12])
        Tail.gauge_return(b, carry, gauge)
        rec['E'] = Ep; rec['mz'] = mz
        ext.closing(b, heads, carry, rec)
        b.x(carry[0]); b.free(carry); inst['Public'].emit(b, S, True)
elif a.mode.startswith('p') and a.mode.endswith('rt'):
    # lane dqi_v8b: staged round trips of the v8 key prefix (p1rt: extractor 0..32 + gauge + chain A)
    import endnode as EN
    ext = inst['ext']; Tail = ext.Tail
    inst['Public'].emit(b, S)
    heads = [km.array([*S[2 * i], *S[2 * i + 1]]) for i in range(33)]
    carry = b.alloc_qubits(24); b.x(carry[0]); info['carry'] = [q.id for q in carry]
    rec = ext.prefix(b, heads, carry)
    gauge = Tail.gauge_prefix(b, carry)
    lam = carry[:12]
    mA = EN.scale_words(b, [S[66], S[67]], lam)
    PA = EN.Pass(CE.SLOT_NODE, True)
    nA, dA, eA = PA.forward(b, heads, S[66], lam, S[67])
    if NEG: b.x(nA[3])
    PA.reverse(b, heads, nA, dA, eA)
    EN.unscale_words(b, [S[66], S[67]], lam, mA)
    Tail.gauge_return(b, carry, gauge)
    ext.closing(b, heads, carry, rec)
    b.x(carry[0]); b.free(carry); inst['Public'].emit(b, S, True)
elif a.mode in ('ext', 'extrt'):
    inst['Public'].emit(b, S)
    heads = [km.array([*S[2 * i], *S[2 * i + 1]]) for i in range(35)]
    carry = b.alloc_qubits(24); b.x(carry[0]); info['carry'] = [q.id for q in carry]
    rec = inst['ext'].prefix(b, heads, carry)
    info['flag'] = rec['tail'].current.id
    if a.mode == 'extrt':
        rec['tail'].release_spare(); rec['tail'].resume_return()
        inst['ext'].closing(b, heads, carry, rec, stage=(lambda m: b.info_tag('@stage:' + m)) if TAGGED else (lambda _: None))
        b.x(carry[0]); b.free(carry); inst['Public'].emit(b, S, True)
elif a.mode == 'key':
    key = inst['prefix'](b, S)
    info['carry'] = [q.id for q in key['carry']]
    inst['closing'](b, key)
elif a.mode == 'fulltag':
    # Same gates as 'full', plus INFO_TAG stage markers (no effect on simulation) for width analysis.
    def wrap(mod, name, tag):
        f = getattr(mod, name)
        def g(builder, *args, **kw):
            b.info_tag(f'@enter:{tag}'); r = f(builder, *args, **kw); b.info_tag(f'@exit:{tag}'); return r
        setattr(mod, name, g)
    ext = inst['ext']
    for nm, tag in (('prefix', 'extract_fwd'), ('closing', 'extract_ret')):
        f0 = getattr(ext, nm)
        def mk(f0, tag):
            def g(*args, **kw):
                b.info_tag(f'@enter:{tag}'); r = f0(*args, **kw); b.info_tag(f'@exit:{tag}'); return r
            return g
        setattr(ext, nm, mk(f0, tag))
    wrap(V7, 'emit_key_prefix', 'key_fwd'); wrap(V7, 'emit_key_closing', 'key_ret')
    kp0 = V7.emit_key_prefix
    def kp(builder, *args, **kw):
        r = kp0(builder, *args, **kw); info['g'] = r['gauge'].flag.id; info['carry'] = [q.id for q in r['carry']]; return r
    V7.emit_key_prefix = kp
    wrap(V7.NewOuter, 'emit_prefix', 'conversion_fwd'); wrap(V7.P.Finish, 'emit_prefix', 'finish_fwd')
    wrap(V7.Adaptive, 'emit_scan', 'scan'); wrap(V7.P.Finish, 'emit_closing_keep_inverse', 'finish_ret')
    wrap(V7.P.Seam, 'outer_closing_with_inverse', 'conversion_ret')
    import scalar_seed_padded as SeedMod
    E = [b.create_classical_register(12, f"E{i}") for i in range(4095)]
    V7.emit(b, S, E, j_min=15, scan_positions=4095, stage=lambda m: None)
    assert b.num_allocated_qubits == 840, b.num_allocated_qubits
elif a.mode == 'census':
    # lane dqi_close: full decoder with INFO_TAG markers around every call of a function whose name contains
    # 'phase', 'closing', 'restore', 'divide' or 'inverse' (args: qubit arrays as first-id:length), plus stages.
    KEYS = ('phase', 'closing', 'restore', 'divide', 'inverse', 'quotient', 'erase', 'repay')
    def desc(v):
        try:
            if isinstance(v, (km.array, list, tuple)) and len(v) and all(isinstance(x, km.q) for x in v):
                return f'{v[0].id}:{len(v)}'
        except Exception:
            pass
        return '.'
    def prof(frame, event, arg):
        if event not in ('call', 'return'): return
        co = frame.f_code; nm = co.co_name
        if nm.startswith('<') or not any(k in nm for k in KEYS): return
        if event == 'call':
            fl = frame.f_locals
            ar = ','.join(desc(fl[v]) for v in co.co_varnames[:co.co_argcount] if v in fl)
            b.info_tag(f'@enter:{nm}|{os.path.basename(co.co_filename)}|{ar}')
        else:
            b.info_tag(f'@exit:{nm}')
    E = [b.create_classical_register(12, f"E{i}") for i in range(4095)]
    sys.setprofile(prof)
    V7.emit(b, S, E, j_min=15, scan_positions=4095, stage=lambda m: b.info_tag(f'@stage:{m}'))
    sys.setprofile(None)
    assert b.num_allocated_qubits == 840, b.num_allocated_qubits
elif a.mode == 'fullw':
    # lane dqi_v8b width probe: v7 full + ONE extra wire live from the end of the key prefix to the key closing
    kp0, kc0 = V7.emit_key_prefix, V7.emit_key_closing
    XW = []
    def kp(builder, *args, **kw):
        r = kp0(builder, *args, **kw); XW.append(builder.alloc_qubits(1)); return r
    def kc(builder, *args, **kw):
        builder.free(XW.pop()); return kc0(builder, *args, **kw)
    V7.emit_key_prefix, V7.emit_key_closing = kp, kc
    E = [b.create_classical_register(12, f"E{i}") for i in range(4095)]
    V7.emit(b, S, E, j_min=15, scan_positions=4095, stage=lambda m: None)
elif a.mode == 'full':
    E = [b.create_classical_register(12, f"E{i}") for i in range(4095)]
    V7.emit(b, S, E, j_min=15, scan_positions=4095, stage=lambda m: None)
    assert b.num_allocated_qubits == 840, b.num_allocated_qubits
c = b.finish_circuit()
fmt = 'kmb' if a.mode in ('full', 'fullw') else 'kmx'
c.to_file(str(a.out / f'{a.mode}.{fmt}'), format=fmt)
info.update(closing_census=dict(sorted(NPC.CENSUS.items())), np=a.np)
info.update(num_qubits=c.num_qubits, static_toffoli_like=c.operation_statistics().num_toffoli_like,
            seconds=round(time.time() - T0, 1))
(a.out / 'wires.json').write_text(json.dumps(info))
print('BUILT', json.dumps({k: v for k, v in info.items() if k not in ('S',)}), flush=True)
