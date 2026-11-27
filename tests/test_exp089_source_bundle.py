"""Preflight the source-only QV2 DQI port and its nested source archives."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/dqi/qv2_m4"


def file_sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main() -> None:
    manifest = json.loads((SOURCE / "MANIFEST.json").read_text(encoding="utf-8"))
    expected = manifest["files"]
    actual = {
        path.relative_to(SOURCE).as_posix()
        for path in SOURCE.rglob("*")
        if path.is_file() and path.name != "MANIFEST.json"
    }
    assert actual == set(expected)
    for name, digest in expected.items():
        path = SOURCE.joinpath(*PurePosixPath(name).parts)
        assert file_sha256(path) == digest
        assert path.suffix.lower() not in {".kmb", ".kmx", ".npz"}

    nested = (
        SOURCE / "kit/repo/runs/20261119T035200Z-dqi-split-finish/jet_terminal17_kit/source_zip",
        SOURCE / "kit/repo/tools/dqi_public_syed_v12/dqi_source_zip",
    )
    for path in nested:
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None
            for info in archive.infolist():
                member = PurePosixPath(info.filename)
                assert not member.is_absolute() and ".." not in member.parts and "\\" not in info.filename
                assert not stat.S_ISLNK(info.external_attr >> 16)
                assert member.suffix.lower() not in {".kmb", ".kmx", ".npz"}
    print("exp-089 source bundle: PASS")


if __name__ == "__main__":
    main()
