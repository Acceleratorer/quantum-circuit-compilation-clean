"""Private root-conditioned Forney phase gate screen.

Embedded into the Kaggle script by build_private_kernel.py for this gate only.
"""

import importlib
from random import Random
import numpy as np


class QubitControlledPhaseBuilder(QubitControlledBuilder):
    """Add one coherent control to field arithmetic and its phase gates."""

    def cz(self, qubit, bit):
        self.base.ccz(self.control, qubit, bit)

    def ccz(self, left, middle, target):
        scratch = self.and_scratch
        self.base.ccx(self.control, left, scratch)
        self.base.ccz(scratch, middle, target)
        self.base.ccx(self.control, left, scratch)

    def __getattr__(self, name):
        return getattr(self.base, name)


def run_root_conditioned_phase_gate_screen(km=None, ar=None):
    """Measure derivative-corrected FMA phases only at denominator roots."""
    if km is None or ar is None:
        km, ar = load_gate_arithmetic()
    _, _, phase_inverse36_pivot = load_width_helpers(km)
    scanner = importlib.import_module("exp.scan.scan")
    common = importlib.import_module("common")
    extract = importlib.import_module("exp.decoder.extract")
    multiply = common.mul
    polynomial_multiply = common.pmul

    def evaluate(poly, point):
        value = 0
        for coefficient in reversed(poly):
            value = multiply(value, point) ^ coefficient
        return value

    weights = (31, 35)
    rng = Random(0xA66063)
    data_node = [1]
    for point in range(70):
        data_node = polynomial_multiply(data_node, [point, 1])

    alpha = common.gf.primitive_element
    powers = [common.power(alpha, index) for index in range(4095)]
    node_values = set(range(1, 70))
    node_positions = {
        index for index, value in enumerate(powers) if value in node_values
    }
    skipped_nodes = set(range(70)) | node_positions
    allowed_positions = [
        index for index in range(4095) if index not in skipped_nodes
    ]
    _, kappas, _, _ = extract.constants(35)

    cases = []
    process_positions = set()
    for weight in weights:
        positions = rng.sample(allowed_positions, weight)
        errors = {
            powers[index]: rng.randrange(1, 1 << FIELD_BITS)
            for index in positions
        }
        locator = [1]
        for root in errors:
            locator = polynomial_multiply(locator, [root, 1])

        evaluator = [0]
        for root, value in errors.items():
            residue = multiply(
                multiply(value, root), evaluate(data_node, root)
            )
            quotient, remainder = common.divmodp(locator[:], [root, 1])
            assert remainder == [0]
            if len(evaluator) < len(quotient):
                evaluator.extend([0] * (len(quotient) - len(evaluator)))
            for index, coefficient in enumerate(quotient):
                evaluator[index] ^= multiply(residue, coefficient)

        padding = [1]
        for index in range(weight + 1, 35, 2):
            padding = polynomial_multiply(padding, [kappas[index], 1, 1])
        numerator = polynomial_multiply(evaluator, padding)
        denominator = polynomial_multiply(locator, padding)
        assert len(numerator) <= 35 and len(denominator) == 36
        assert denominator[-1] == 1

        error_positions = {
            next(index for index, value in enumerate(powers) if value == root): value
            for root, value in errors.items()
        }
        denominator_roots = [
            index
            for index, beta in enumerate(powers)
            if index not in skipped_nodes and evaluate(denominator, beta) == 0
        ]
        process_positions.update(denominator_roots)
        cases.append(
            {
                "weight": weight,
                "pair": (
                    numerator + [0] * (35 - len(numerator)),
                    denominator[:35],
                ),
                "denominator": denominator,
                "error_positions": error_positions,
                "error_root_count": len(errors),
            }
        )

    process_positions = sorted(process_positions)
    assert all(
        set(case["error_positions"]).issubset(process_positions) for case in cases
    )
    mask_values = {
        position: [rng.randrange(1 << FIELD_BITS) for _ in cases]
        for position in process_positions
    }
    expected_phases = [
        sum(
            (value & mask_values[position][case_index]).bit_count()
            for position, value in case["error_positions"].items()
        )
        & 1
        for case_index, case in enumerate(cases)
    ]

    def build_gate(corrected):
        builder = km.CircuitBuilder()
        numerator_words = [builder.alloc_qubits(FIELD_BITS) for _ in range(35)]
        denominator_words = [builder.alloc_qubits(FIELD_BITS) for _ in range(35)]
        input_masks = {
            position: builder.alloc_bits(FIELD_BITS)
            for position in process_positions
        }
        phase_mask = builder.alloc_bits(FIELD_BITS)

        for position in process_positions:
            beta = powers[position]
            beta_powers = [1]
            for _ in range(34):
                beta_powers.append(multiply(beta_powers[-1], beta))
            leading = multiply(beta_powers[-1], beta)

            numerator_columns = [
                [multiply(beta_powers[k], 1 << bit) for bit in range(FIELD_BITS)]
                for k in range(1, 35)
            ]
            denominator_columns = numerator_columns
            for k, columns in enumerate(numerator_columns, start=1):
                ar.linear_xor(
                    builder, numerator_words[k], numerator_words[0], columns
                )
                ar.linear_xor(
                    builder, denominator_words[k], denominator_words[0], columns
                )
            xor_constant(builder, denominator_words[0], leading)
            ladder = scanner.zero_hold(builder, denominator_words[0])
            root_flag = ladder[-1]

            if corrected:
                derivative = builder.alloc_qubits(FIELD_BITS)
                for k in range(1, 35, 2):
                    columns = [
                        multiply(beta_powers[k - 1], 1 << bit)
                        for bit in range(FIELD_BITS)
                    ]
                    ar.linear_xor(
                        builder, denominator_words[k], derivative, columns
                    )
                leading_derivative = beta_powers[34]
                xor_constant(builder, derivative, leading_derivative)

                reciprocal = builder.alloc_qubits(FIELD_BITS)
                control_scratch = builder.alloc_qubits(1)[0]
                controlled = QubitControlledPhaseBuilder(
                    builder, root_flag, control_scratch
                )
                ar.inverse(controlled, derivative, target=reciprocal)

                borrowed = list(builder.alloc_qubits(FIELD_BITS))
                scale_inplace(
                    controlled,
                    numerator_words[0],
                    reciprocal,
                    derivative,
                    borrowed,
                    ar,
                )

            point_value = evaluate(data_node, beta)
            scale = common.inv(multiply(beta, point_value))
            if not scale:
                raise AssertionError("selected scan point is a sample node")
            mask = input_masks[position]
            builder.bit_store(phase_mask, False)
            for bit in range(FIELD_BITS):
                for source_bit in ar.bits(multiply(scale, 1 << bit)):
                    builder.cx(mask[source_bit], phase_mask[bit])
            builder.ccz(root_flag, numerator_words[0], phase_mask)

            if corrected:
                scale_inplace(
                    controlled,
                    numerator_words[0],
                    derivative,
                    reciprocal,
                    borrowed,
                    ar,
                )
                for qubit in borrowed:
                    builder.free(qubit)
                ar.inverse(controlled, derivative, target=reciprocal)
                builder.free(reciprocal)
                builder.free(control_scratch)

                for k in reversed(range(1, 35, 2)):
                    columns = [
                        multiply(beta_powers[k - 1], 1 << bit)
                        for bit in range(FIELD_BITS)
                    ]
                    ar.linear_xor(
                        builder, denominator_words[k], derivative, columns
                    )
                xor_constant(builder, derivative, leading_derivative)
                builder.free(derivative)

            scanner.zero_free(builder, denominator_words[0], ladder)
            xor_constant(builder, denominator_words[0], leading)
            for k in reversed(range(1, 35)):
                ar.linear_xor(
                    builder,
                    denominator_words[k],
                    denominator_words[0],
                    denominator_columns[k - 1],
                )
            for k in reversed(range(1, 35)):
                ar.linear_xor(
                    builder,
                    numerator_words[k],
                    numerator_words[0],
                    numerator_columns[k - 1],
                )

        circuit = builder.finish_circuit()
        return circuit, numerator_words, denominator_words, input_masks

    def simulate(circuit, numerator_words, denominator_words, input_masks, case_index):
        simulator = km.Simulator(
            batch_size=1,
            debug_print=False,
            counting_operations=True,
            seed=0,
        )
        simulator.use_same_registers_as(circuit)
        case = cases[case_index]
        for index, register in enumerate(numerator_words):
            simulator.write_across_shots(
                register, bit_columns([case["pair"][0][index]], FIELD_BITS)
            )
        for index, register in enumerate(denominator_words):
            simulator.write_across_shots(
                register, bit_columns([case["pair"][1][index]], FIELD_BITS)
            )
        all_masks = km.array(
            [bit for position in process_positions for bit in input_masks[position]]
        )
        mask_bits = np.stack(
            [
                np.full(1, (mask_values[position][case_index] >> bit) & 1, dtype=bool)
                for position in process_positions
                for bit in range(FIELD_BITS)
            ],
            axis=0,
        )
        simulator.write_across_shots(all_masks, mask_bits)
        simulator.do(circuit)

        observed_phase = int(simulator.read_phase_flipped_across_shots()[0])
        restore_errors = 0
        for index, register in enumerate(numerator_words):
            restore_errors += not np.array_equal(
                simulator.read_across_shots(register),
                bit_columns([case["pair"][0][index]], FIELD_BITS),
            )
        for index, register in enumerate(denominator_words):
            restore_errors += not np.array_equal(
                simulator.read_across_shots(register),
                bit_columns([case["pair"][1][index]], FIELD_BITS),
            )
        restore_errors += not np.array_equal(simulator.read_across_shots(all_masks), mask_bits)

        live = set().union(
            *(set(register) for register in numerator_words + denominator_words)
        )
        scratch = [
            km.q(index) for index in range(circuit.num_qubits) if km.q(index) not in live
        ]
        scratch_clean = not scratch or not np.any(
            simulator.read_across_shots(km.array(scratch))
        )
        return {
            "phase": observed_phase,
            "phase_error": observed_phase != expected_phases[case_index],
            "restore_errors": int(restore_errors),
            "scratch_clean": bool(scratch_clean),
            "dynamic_toffoli_like": simulator.operation_statistics().num_toffoli_like,
            "compiled_qubits": circuit.num_qubits,
        }

    baseline_circuit, baseline_a, baseline_b, baseline_masks = build_gate(False)
    corrected_circuit, corrected_a, corrected_b, corrected_masks = build_gate(True)
    rows = []
    for case_index, case in enumerate(cases):
        baseline = simulate(
            baseline_circuit, baseline_a, baseline_b, baseline_masks, case_index
        )
        corrected_result = simulate(
            corrected_circuit, corrected_a, corrected_b, corrected_masks, case_index
        )
        rows.append(
            {
                "weight": case["weight"],
                "denominator_roots": len(case["error_positions"]),
                "expected_phase": expected_phases[case_index],
                "observed_phase": corrected_result["phase"],
                "phase_errors": int(corrected_result["phase_error"]),
                "restore_errors": corrected_result["restore_errors"],
                "scratch_clean": corrected_result["scratch_clean"],
                "baseline_dynamic_t": baseline["dynamic_toffoli_like"],
                "corrected_dynamic_t": corrected_result["dynamic_toffoli_like"],
                "added_dynamic_t": (
                    corrected_result["dynamic_toffoli_like"]
                    - baseline["dynamic_toffoli_like"]
                ),
                "compiled_qubits": corrected_result["compiled_qubits"],
            }
        )

    added_mean_t = sum(row["added_dynamic_t"] for row in rows) / len(rows)
    tie_budget_mean_t = 34837.5678948333
    phase_errors = sum(row["phase_errors"] for row in rows)
    restore_errors = sum(row["restore_errors"] for row in rows)
    clean_scratch = all(row["scratch_clean"] for row in rows)
    peak_qubits = max(row["compiled_qubits"] for row in rows)
    status = (
        "PASS"
        if phase_errors == 0
        and restore_errors == 0
        and clean_scratch
        and peak_qubits <= 890
        and added_mean_t <= tie_budget_mean_t
        else "FAIL_GATE"
    )
    return {
        "experiment": "exp-057-root-conditioned-forney-phase-gate",
        "status": status,
        "weights": list(weights),
        "processed_denominator_roots": len(process_positions),
        "rows": rows,
        "checks": {
            "phase_errors": phase_errors,
            "restore_errors": restore_errors,
            "scratch_clean": clean_scratch,
            "peak_qubits": peak_qubits,
            "width_gate": 890,
            "added_mean_t": added_mean_t,
            "tie_budget_mean_t": tie_budget_mean_t,
        },
        "identity": "At each simple root beta, A(beta)=omega(beta)*padding(beta), B'(beta)=sigma'(beta)*padding(beta), and omega(beta)/(beta*P(beta)*sigma'(beta)) is the error value.",
        "scope": "Private gate only at all denominator roots from one seeded weight-31 and one seeded weight-35 case; sample-node branch, full 4095-point build, integrated FMA schedule, and official verifier are omitted.",
    }
