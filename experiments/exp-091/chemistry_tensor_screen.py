"""Static rank screen for the tracked V22 chemistry loader payload.

The script reads payload bytes and performs GF(2) linear algebra. It never
imports or executes an upstream notebook or circuit builder.
"""
from __future__ import annotations

import base64
import json
from pathlib import Path

import numpy as np


PAYLOAD = Path(__file__).resolve().parent.parent / "exp-082" / "module" / "payload" / "v22_loader_programs.b85"
LOADERS = ((2, 131, 0, 5, 13), (3, 130, 0, 7, 3), (4, 131, 0, 3, 7),
           (6, 131, 0, 4, 11), (8, 123, 0, 11, 4), (9, 130, 0, 13, 7),
           (10, 130, 0, 7, 6), (12, 127, 0, 6, 8), (13, 124, 0, 11, 3),
           (14, 124, 0, 6, 9))


def rank(a: np.ndarray) -> int:
    a = a.copy().astype(np.uint8)
    rows, cols, out = a.shape[0], a.shape[1], 0
    for col in range(cols):
        pivot = np.flatnonzero(a[out:, col])
        if not len(pivot):
            continue
        pivot = int(pivot[0]) + out
        a[[out, pivot]] = a[[pivot, out]]
        for row in range(out + 1, rows):
            if a[row, col]:
                a[row] ^= a[out]
        out += 1
        if out == rows:
            break
    return out


def inverse(a: np.ndarray) -> np.ndarray:
    n = a.shape[0]
    work = np.concatenate((a.copy().astype(np.uint8), np.eye(n, dtype=np.uint8)), axis=1)
    for col in range(n):
        pivot = np.flatnonzero(work[col:, col])
        if not len(pivot):
            raise ValueError("singular matrix")
        pivot = int(pivot[0]) + col
        work[[col, pivot]] = work[[pivot, col]]
        for row in range(n):
            if row != col and work[row, col]:
                work[row] ^= work[col]
    return work[:, n:]


def mm(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return ((a.astype(np.uint16) @ b.astype(np.uint16)) & 1).astype(np.uint8)


def take(blob: bytes, position: int, shape: tuple[int, ...]) -> tuple[np.ndarray, int]:
    size = int(np.prod(shape))
    end = position + size
    return np.frombuffer(blob[position:end], dtype=np.uint8).reshape(shape).copy(), end


def slices(left: np.ndarray, right: np.ndarray, mask: np.ndarray) -> list[np.ndarray]:
    width = left.shape[1]
    result = []
    for out in range(mask.shape[1]):
        matrix = np.zeros((width, width), dtype=np.uint8)
        for u, v, term_mask in zip(left, right, mask):
            if term_mask[out]:
                matrix ^= np.outer(u, v)
        result.append(matrix)
    return result


def pencil_test(parts: list[np.ndarray], trials: int, seed: int) -> dict[str, int | bool]:
    width = parts[0].shape[0]
    rng = np.random.default_rng(seed)
    full_rank = idempotent_fail = commute_fail = 0
    for _ in range(trials):
        selector = rng.integers(0, 2, len(parts), dtype=np.uint8)
        chosen = np.zeros((width, width), dtype=np.uint8)
        for bit, part in zip(selector, parts):
            if bit:
                chosen ^= part
        if rank(chosen) != width:
            continue
        full_rank += 1
        chosen_inv = inverse(chosen)
        operators = [mm(part, chosen_inv) for part in parts]
        if any(not np.array_equal(mm(op, op), op) for op in operators):
            idempotent_fail += 1
            continue
        if any(not np.array_equal(mm(operators[i], operators[j]), mm(operators[j], operators[i]))
               for i in range(len(operators)) for j in range(i)):
            commute_fail += 1
            continue
        return {"trials": trials, "full_rank_trials": full_rank,
                "idempotent_failures": idempotent_fail,
                "commutation_failures": commute_fail, "rank99_witness": True}
    return {"trials": trials, "full_rank_trials": full_rank,
            "idempotent_failures": idempotent_fail,
            "commutation_failures": commute_fail, "rank99_witness": False}


def scan() -> dict:
    blob = base64.b85decode(PAYLOAD.read_text(encoding="ascii").replace("\n", ""))
    position = 0
    reports = []
    for loader, products, early, _c1, _c2 in LOADERS:
        features = 100 if early else 99
        _ands, position = take(blob, position, (68, 6))
        _bank, position = take(blob, position, (9 if early else 8, 10))
        left_raw, position = take(blob, position, (products, 13))
        right_raw, position = take(blob, position, (products, 13))
        mask_raw, position = take(blob, position, (products, 4))
        _rest, position = take(blob, position, (30, 13))
        left = np.unpackbits(left_raw, axis=1)[:, :features]
        right = np.unpackbits(right_raw, axis=1)[:, :features]
        mask = np.unpackbits(mask_raw, axis=1)[:, :30]
        pairs = {(tuple(np.flatnonzero(u)), tuple(np.flatnonzero(v))) for u, v in zip(left, right)}
        part = slices(left, right, mask)
        reports.append({
            "loader": loader,
            "product_terms": products,
            "unique_product_pairs": len(pairs),
            "left_flattening_rank": rank(np.concatenate(part, axis=1)),
            "right_flattening_rank": rank(np.concatenate([matrix.T for matrix in part], axis=1)),
            "rank99_pencil": pencil_test(part, trials=128, seed=20261128 + loader),
        })
    # The four compressed base-loader payloads are part of the blob but are not
    # decoded by this screen; only their declared byte lengths are needed.
    position += sum((20881, 20896, 20978, 20826))
    assert position == len(blob)
    return {"status": "NO_GO_RANK99_PENCIL", "payload_bytes": len(blob),
            "custom_loader_count": len(reports),
            "custom_product_terms": sum(r["product_terms"] for r in reports),
            "rank99_product_savings_ceiling": sum(r["product_terms"] - min(
                r["left_flattening_rank"], r["right_flattening_rank"]) for r in reports),
            "chemistry_gate": {
                "baseline_cost": 249853852.96142676,
                "required_cost_at_qv2_projection": 204476813.8348401,
                "required_reduction_fraction": 0.1816,
            },
            "loaders": reports}


if __name__ == "__main__":
    result = scan()
    assert result["status"] == "NO_GO_RANK99_PENCIL"
    assert all(r["product_terms"] == r["unique_product_pairs"] for r in result["loaders"])
    assert not any(r["rank99_pencil"]["rank99_witness"] for r in result["loaders"])
    print(json.dumps(result, indent=2))
