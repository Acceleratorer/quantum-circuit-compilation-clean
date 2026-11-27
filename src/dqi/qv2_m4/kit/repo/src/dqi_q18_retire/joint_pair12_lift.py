"""One fixed seven-point GF8 lift of the published joint rank7 tensor.

Input coordinates and interpolation points exactly match incumbent tensor(12).
An inconsistent linear system yields a directly checkable dual certificate.
No alternative basis, random search, SAT, or point-set sweep is performed.
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
from dqi_q18_retire import published_joint_gate as base


def write(run, name, value):
    (run/(name+'.json')).write_text(json.dumps(value, indent=2)+'\n')
    print(json.dumps(value), flush=True)


def solve(rows, outputs, terms):
    piv = {}
    for i, (row, output) in enumerate(zip(rows, outputs)):
        combination = 1 << i
        while row:
            p = row.bit_length()-1
            if p not in piv:
                piv[p] = row, output, combination
                break
            a, b, c = piv[p]
            row ^= a; output ^= b; combination ^= c
        if not row and output:
            assert xor(rows[j] for j in base.bits(combination)) == 0
            assert xor(outputs[j] for j in base.bits(combination)) == output
            return dict(spans=False, equation_indices=base.bits(combination), nonzero_output=output)
    result = [0]*terms
    for p, (row, output, _) in sorted(piv.items()):
        result[p] = output ^ xor(result[j] for j in base.bits(row ^ (1 << p)))
    assert all(xor(result[j] for j in base.bits(row)) == output for row, output in zip(rows, outputs))
    return dict(spans=True, output_vectors=result, feature_rank=len(piv))


def xor(values):
    z = 0
    for v in values: z ^= v
    return z


def forms():
    ref = base.source.load(); ar, f, s = ref['ar'], ref['f12'], ref['ar'].field(3)
    generator = f.pow(f.primitive_element, 4095//7)
    def polynomial(value, p):
        out = 0
        for i in reversed(range(4)): out = f.mul(out, p) ^ (value >> i & 1)
        return out
    root = next(f.pow(generator, i) for i in range(1, 8) if polynomial(s.modulus, f.pow(generator, i)) == 0)
    embed = [f.pow(root, i) for i in range(3)]
    columns = [f.mul(embed[i], f.pow(f.primitive_element, j)) for j in range(4) for i in range(3)]
    inv = ar.inverse_columns(columns)
    published = json.loads((ROOT/'runs/20261031T215700Z-published-joint-source-loader/construct.json').read_text())['terms']
    pulled, original_masks = [], []
    for point in list(range(6))+[None]:
        values = []
        for co in inv:
            v = (co >> 9) & 7 if point is None else 0
            if point is not None:
                for j in reversed(range(4)): v = s.mul(v, point) ^ ((co >> (3*j)) & 7)
            values.append(v)
        pull = lambda mask: sum(((mask & v).bit_count() & 1) << i for i, v in enumerate(values))
        original_masks += [pull(mask) for mask, _ in ar.tensor(3)]
        pulled += [(pull(a), pull(b)) for a, b, _ in published]
    assert original_masks == [mask for mask, _ in ar.tensor(12)]
    assert len(pulled) == 49
    return ref, pulled, columns


def gate(run):
    ref, pulled, columns = forms(); f = ref['f12']
    rows = [sum(((a >> i & 1) & (b >> j & 1)) << k for k, (a, b) in enumerate(pulled))
            for i in range(12) for j in range(12)]
    ordinary = [f.mul(1 << i, 1 << j) for i in range(12) for j in range(12)]
    target = [ordinary[12*i+j] | (f.mul(1 << i, f.square(1 << j)) << 12)
              for i in range(12) for j in range(12)]
    control = solve(rows, ordinary, 49); assert control['spans']
    result = solve(rows, target, 49)
    result.update(status='PASS_FIXED_PUBLISHED_LIFT_GATE', evidence='diagnostic',
                  points=[0, 1, 2, 3, 4, 5, None], columns=columns, forms=pulled,
                  all_144_ordinary_product_equations=True,
                  GF12_modulus=f.modulus, GF8_modulus=ref['ar'].field(3).modulus,
                  hypothesized_full_saving_T=2034, utility_threshold_T=1000,
                  scope='Only the actual incumbent quartic GF8 coordinates and seven points with the fixed published rank7 local tensor. A failed span is not a GF12 Frobenius-pair rank lower bound.')
    if result['spans']:
        terms = [(a, b, w) for (a, b), w in zip(pulled, result['output_vectors']) if w]
        (run/'pair12_terms.json').write_text(json.dumps(terms)+'\n')
        result['actual_pair_rank'] = len(terms)
    write(run, 'gate', result)


def lifted_terms(ref, pair, c):
    f, K, n, terms = ref['f12'], 2048, 12, []
    singles = [(m, m, w) for m, w in ref['ar'].tensor(12)]
    def add(body, xoff, yoff, out0, out1=None, both=False, sq=False):
        for a, b, w in body:
            x = (a << xoff) ^ ((a << 12) if both else 0)
            if sq: b = sum(((b & f.square(1 << j)).bit_count() & 1) << j for j in range(12))
            y = (b << yoff) ^ ((b << 12) if both else 0)
            z = xor(f.mul(co, w & 4095) << (12*j) for j, co in enumerate(out0))
            if out1: z ^= xor(f.mul(co, w >> 12) << (12*j) for j, co in enumerate(out1))
            if z: terms.append((x, y, z))
    if c:
        ck = f.mul(c, K)
        add(pair, 0, 0, [1, 1, 0, 0], [0, 0, c ^ 1, c])
        add(pair, 12, 12, [K, 0, 0, 0], [0, 0, ck ^ K ^ 1, ck ^ 1])
        add(pair, 0, 0, [0, 1, 0, 0], [0, 0, 1, c], both=True)
        if ck != 1: add(singles, 0, 12, [0, 0, ck ^ 1, 0], sq=True)
    else:
        add(singles, 0, 0, [1, 1, 0, 0])
        add(pair, 12, 12, [K, 0, 0, 0], [0, 0, K, 1])
        add(singles, 0, 0, [0, 1, 0, 0], both=True)
        add(singles, 12, 0, [0, 0, 1, 0], sq=True)
    return terms


def component(run):
    g = json.loads((run/'gate.json').read_text()); assert g['spans']
    pair = json.loads((run/'pair12_terms.json').read_text()); ref = base.source.load()
    counts = {0: 198, **dict(ref['contexts']())}; tensors = {}; bill = 0
    for c, count in counts.items():
        tensor = lifted_terms(ref, pair, c)
        assert ref['coefficients'](tensor) == ref['target'](c, quadratic=True)
        tensors[c] = tensor; bill += count * len(tensor)
    assert 77508-bill >= 1000
    (run/'actual_joint_tensors.json').write_text(json.dumps(tensors)+'\n')
    write(run, 'component', dict(status='PASS_EXPLICIT_FULL_SOURCE_TENSORS', evidence='diagnostic',
          all_source_c=len(tensors), all_basis_pairs=len(tensors)*576, joint_pool_T=bill,
          saving_T=77508-bill, privateQ=0,
          next='Native dirty-target and frozen whole-source constructor required before evaluation or promotion.'))


def close(run):
    g = json.loads((run/'gate.json').read_text()); assert not g['spans']
    ref, pulled, columns = forms(); f = ref['f12']
    rows = [sum(((a >> i & 1) & (b >> j & 1)) << k for k, (a, b) in enumerate(pulled))
            for i in range(12) for j in range(12)]
    target = [f.mul(1 << i, 1 << j) | (f.mul(1 << i, f.square(1 << j)) << 12)
              for i in range(12) for j in range(12)]
    assert columns == g['columns']
    assert xor(rows[i] for i in g['equation_indices']) == 0
    assert xor(target[i] for i in g['equation_indices']) == g['nonzero_output'] != 0
    write(run, 'terminal', dict(status='DONE_FIXED_SEVEN_POINT_LIFT_REJECTED', evidence='diagnostic',
          exact_dual_certificate_rechecked=True, equation_indices=g['equation_indices'],
          nonzero_output=g['nonzero_output'], utility_threshold_T=1000,
          source_tower_identity_still_valid=True, production_candidate_emitted=False,
          scope=g['scope'], next='Requires a distinct explicit full GF12 Frobenius-pair tensor, not a larger sample or unchanged basis rerun.'))


if __name__ == '__main__':
    mode, run = sys.argv[1], Path(sys.argv[2])
    {'gate': gate, 'component': component, 'close': close}[mode](run)
