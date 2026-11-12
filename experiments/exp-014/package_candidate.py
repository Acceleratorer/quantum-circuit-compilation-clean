"""Build a deterministic Kaggle submission ZIP from verified local members."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile


EXPECTED_ANGLE_COUNT = 15


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def members(args: argparse.Namespace) -> list[tuple[str, Path]]:
    entries = [("invsqrt.kmb", args.invsqrt), ("dqi.kmb", args.dqi)]
    # Keep the archive order stable across PowerShell and POSIX runs.
    angles = sorted(args.chem_dir.glob("angle_k_*.kmb"), key=lambda p: p.name)
    if len(angles) != EXPECTED_ANGLE_COUNT:
        raise SystemExit(f"expected {EXPECTED_ANGLE_COUNT} angle_k_*.kmb files, found {len(angles)}")
    entries.extend((f"dfthcsos/{p.name}", p) for p in angles)
    npz = args.chem_dir / "submission.npz"
    entries.append(("dfthcsos/submission.npz", npz))
    for name, path in entries:
        if not path.is_file():
            raise SystemExit(f"missing member: {name} ({path})")
    if len({name for name, _ in entries}) != len(entries):
        raise SystemExit("duplicate archive member")
    return entries


def build(args: argparse.Namespace) -> dict[str, object]:
    out = args.out.resolve()
    if out.exists() and not args.force:
        raise SystemExit(f"refusing to overwrite {out}; pass --force to replace it")
    entries = members(args)
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, path in entries:
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, path.read_bytes())
    data = out.read_bytes()
    receipt = {
        "archive_sha256": sha256(data),
        "members": {name: sha256(path.read_bytes()) for name, path in entries},
        "member_count": len(entries),
    }
    if args.receipt:
        args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--invsqrt", type=Path, required=True)
    parser.add_argument("--dqi", type=Path, required=True)
    parser.add_argument("--chem-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    print(json.dumps(build(args), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
