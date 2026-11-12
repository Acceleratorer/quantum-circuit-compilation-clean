"""Preflight the exp-017 negative-result receipt."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RECEIPT=ROOT/'experiments'/'exp-017'/'receipt.json'
def main():
    r=json.loads(RECEIPT.read_text(encoding='utf-8'))
    assert r['candidate_id']=='v13-64d0-retention-hybrid'
    assert r['member_sha256']['dqi.kmb'].startswith('64d0c2f9')
    assert len(r['member_sha256']['dqi.kmb'])==hashlib.sha256().digest_size*2
    assert r['member_verification']['dqi']['verified_shots']==102400
    assert r['member_verification']['dqi']['phase_errors']==2
    assert r['member_verification']['dqi']['value_errors']==0
    assert r['local_geometric_mean'] < r['comparison']['primary_local_geometric_mean']
    print('retention negative receipt: PASS')
if __name__=='__main__': main()
