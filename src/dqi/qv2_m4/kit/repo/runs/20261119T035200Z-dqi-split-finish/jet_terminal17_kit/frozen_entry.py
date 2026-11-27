"""Rebuild the private rank-62 fused/paid grade-17 decoder inside its licensed sandbox."""
from pathlib import Path
import hashlib
import json
import sys
import zipfile

here=Path(__file__).resolve().parent
repo=here.parents[2]
out=Path(sys.argv[sys.argv.index('--out')+1])
frozen=out/'fixed_input'
archive=here/'source.zip'
want='5aa1727788f0d7911bc1b7ff73095d009b11bd6381aa719bcfc73a87e13dfbc5'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==want
hashes=json.loads((here/'sources.json').read_text())['files']
with zipfile.ZipFile(archive) as z:
    assert set(z.namelist())==set(hashes)
    for name,sha in hashes.items():
        data=z.read(name)
        assert hashlib.sha256(data).hexdigest()==sha
        dst=frozen/name
        dst.parent.mkdir(exist_ok=True,parents=True)
        dst.write_bytes(data)

def attach_parent_inputs(original,dest):
    for item in original.iterdir():
        if item.name.startswith('.'):continue
        local=dest/item.name
        if not local.exists():
            local.symlink_to(item,target_is_directory=item.is_dir())
        elif local.is_dir():
            attach_parent_inputs(item,local)

for name in ('runs','src','tools'):attach_parent_inputs(repo/name,frozen/name)
for name in ('official','data'):
    (frozen/name).symlink_to(repo/name,target_is_directory=True)
source=frozen/'runs/20261119T035200Z-dqi-split-finish/terminal_jet_latest.py'
sys.argv.extend('--rank62 --norm-pay --first-tail 17 --native-seed --terminal-guard --unconditional-scalar --cut 15 --base joint --variant timed-mask --consume-units --fuse-phase'.split())
exec(compile(source.read_text(),str(source),'exec'),dict(__name__='__main__',__file__=str(source)))
