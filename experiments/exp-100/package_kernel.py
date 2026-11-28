"""Stage exp-100's private Kaggle kernel."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.file_digest(path.open("rb"), "sha256").hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    out = parser.parse_args().output_dir.resolve()
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"staging directory must be empty: {out}")
    out.mkdir(parents=True, exist_ok=True)
    for name in ("main.py", "kernel-metadata.json"):
        src = HERE / name
        dst = out / name
        dst.write_bytes(src.read_bytes())
    print(json.dumps({"staging_dir": str(out), "main_sha256": sha256(out / "main.py")}, indent=2))


if __name__ == "__main__":
    main()
