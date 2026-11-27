"""Qualify one published GF8 joint tensor against the actual GF24 API.

The seven exponent pairs are from Bartoli, Zini, Zullo, arXiv:2201.08242v1,
Table 1, n=3,k=2,q=2, licensed CC BY 4.0. The trace-dual conversion,
binary emitter and source-contract tests below are independently implemented.
This is not a general GF24 tensor search or a lower-bound argument.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'official/2026-10-27/kickmix')]
import kickmix as km
import numpy as np
from dqi_q18_retire import joint_basis_gate as source

PAIRS = ((2, 0), (3, 5), (1, 2), (0, 4), (6, 6), (5, 1), (4, 3))


def bits(x):
    return [i for i in range(x.bit_length()) if x >> i & 1]


def write(run, name, data):
    (run / (name + '.json')).write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps(data), flush=True)


def evaluate(terms, a, b):
    out = 0
    for x, y, z in terms:
        if ((x & a).bit_count() & 1) and ((y & b).bit_count() & 1):
            out ^= z
    return out


def construct(run):
    f = km.GF2Field(3)
    assert f.modulus == 11 and f.primitive_element == 2
    def trace(x):
        z = x ^ f.square(x) ^ f.square(f.square(x))
        assert z in (0, 1)
        return z
    def mask(x):
        return sum(trace(f.mul(x, 1 << i)) << i for i in range(3))
    forms = [(mask(f.pow(2, i)), mask(f.pow(2, j))) for i, j in PAIRS]
    pivots = {}
    for i in range(3):
        for j in range(3):
            row = sum(((a >> i & 1) & (b >> j & 1)) << k
                      for k, (a, b) in enumerate(forms))
            rhs = f.mul(1 << i, 1 << j) | (f.mul(1 << i, f.square(1 << j)) << 3)
            while row:
                p = row.bit_length() - 1
                if p not in pivots:
                    pivots[p] = row, rhs
                    break
                row ^= pivots[p][0]
                rhs ^= pivots[p][1]
            if not row:
                assert rhs == 0, 'Published rank-one basis does not span the required pair'
    assert len(pivots) == 7
    outputs = [0] * 7
    for p, (row, rhs) in sorted(pivots.items()):
        for j in bits(row ^ (1 << p)):
            rhs ^= outputs[j]
        outputs[p] = rhs
    terms = [(a, b, z) for (a, b), z in zip(forms, outputs)]
    assert all(z for _, _, z in terms)
    target = lambda a, b: f.mul(a, b) | (f.mul(a, f.square(b)) << 3)
    assert all(evaluate(terms, a, b) == target(a, b) for a in range(8) for b in range(8))
    corrupt = list(terms); a, b, z = corrupt[0]; corrupt[0] = a, b, z ^ 1
    assert any(evaluate(corrupt, a, b) != target(a, b) for a in range(8) for b in range(8))
    lines = []
    for a, b, z in terms:
        ix, iy, iz = bits(a), [3 + i for i in bits(b)], [6 + i for i in bits(z)]
        before = ([f'CX q{i} q{ix[0]}' for i in ix[1:]]
                  + [f'CX q{i} q{iy[0]}' for i in iy[1:]]
                  + [f'CX q{iz[0]} q{i}' for i in iz[1:]])
        lines += before + [f'CCX q{ix[0]} q{iy[0]} q{iz[0]}'] + before[::-1]
    path = run / 'published_gf8_pair.kmx'
    path.write_text('\n'.join(lines) + '\n')
    data = np.arange(4096, dtype=np.uint64)
    states = np.array([((data >> q) & 1) != 0 for q in range(12)])
    expected = data.copy()
    for i, word in enumerate(data):
        value = int(word)
        expected[i] ^= np.uint64(target(value & 7, (value >> 3) & 7) << 6)
    sim = km.Simulator(batch_size=4096, seed=215700, counting_operations=True)
    wires = km.array([km.q(q) for q in range(12)])
    sim.write_across_shots(wires, states)
    sim.do(km.Circuit(path.read_text()))
    actual = sim.read_across_shots(wires)
    assert np.array_equal(actual, np.array([((expected >> q) & 1) != 0 for q in range(12)]))
    assert not np.any(sim.read_phase_flipped_across_shots())
    assert sim.operation_statistics().num_toffoli_like == 7 * 4096
    write(run, 'construct', dict(status='PASS_EXACT_PUBLISHED_GF8_PAIR', evidence='diagnostic',
          terms=terms, exponent_pairs=PAIRS, source_url='https://arxiv.org/html/2201.08242v1',
          license='CC BY 4.0', basis='GF2 polynomial x^3+x+1, primitive2',
          exact_basis_pair_equations=9, all_input_pairs=64, native_dirty_target_cases=4096,
          native_mean_paid_T=7, private_qubits=0, all_phases_zero=True,
          kmx_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
          source_call_replacement_qualified=False))


def bind(run):
    assert json.loads((run / 'construct.json').read_text())['status'] == 'PASS_EXACT_PUBLISHED_GF8_PAIR'
    h = source.load()
    counts = h['contexts']()
    assert sum(counts.values()) == 216
    # Exact source quadratic representation: H=(a,h), high12 is the projection.
    # Any scalar A(H)=kH must have k=c by H=1; H=2^12 then differs by1.
    witnesses = []
    for c in [0] + sorted(counts):
        A = lambda x: h['emul'](c, x) ^ (x >> 12)
        assert A(1) == c
        actual = A(1 << 12)
        scalar = h['emul'](c, 1 << 12)
        assert actual ^ scalar == 1
        witnesses.append(dict(c=c, count=counts.get(c, 198), H=1 << 12, D=1,
                              actual_second=actual, scalar_shared_second=scalar))
    assert len(witnesses) == 32
    write(run, 'binding', dict(status='DIRECT_SHARED_FACTOR_SUBSTITUTION_REJECTED',
          evidence='diagnostic', actual_map='(H*D,(c*H+high12(H))*D^2)',
          field_bits=24, actual_nonzero_c_calls=216, actual_zero_c_calls=198,
          actual_joint_paid_T=77508, witnesses=witnesses,
          qualified_saving_T=0, source_call_replacement_qualified=False,
          scope='Only replacing the complete source pair by one common-first-factor Frobenius-pair tensor with scalar input/output rescaling. Does not rule out a general linear isotopy, alternative interpolation, multi-product composition, or lower-rank GF24 tensor. No current-basis or cap census was repeated.'))


def close(run):
    result = json.loads((run / 'binding.json').read_text())
    assert result['status'] == 'DIRECT_SHARED_FACTOR_SUBSTITUTION_REJECTED'
    write(run, 'terminal', dict(status='DONE_SCOPED_SOURCE_DEPENDENCY', evidence='diagnostic',
          published_tensor_import='PASS', production_lift='UNQUALIFIED',
          complete_candidate_emitted=False, new_method_lower_bound=False,
          next_requirement='An explicit <=41 GF(2^12) tensor, or an exact cheaper tensor for (HD,(cH+high12(H))D^2) with the full source basis transform and charged cleanup.'))


if __name__ == '__main__':
    mode, run = sys.argv[1], Path(sys.argv[2])
    {'construct': construct, 'bind': bind, 'close': close}[mode](run)
