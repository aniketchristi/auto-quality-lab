"""Local review storage with atomic writes and stale-edit protection."""
import hashlib
import json
import os
import tempfile
import fcntl
from datetime import datetime, timezone


def load_packet(path):
    content = path.read_bytes()
    return json.loads(content), hashlib.sha256(content).hexdigest()


def save_review(path, revision, review_id, values):
    required = {'symptom_code', 'component_consistent', 'evidence_specificity',
                'reporting_delay_note', 'review_note'}
    if set(values) != required or not all(isinstance(v, str) for v in values.values()):
        raise ValueError('Review fields must be text and match the expected fields.')
    if not values['symptom_code'].strip():
        raise ValueError('Enter a symptom code, including uncertain if needed.')
    if values['component_consistent'] not in ['yes', 'no', 'uncertain']:
        raise ValueError('Choose a component assessment.')
    if values['evidence_specificity'] not in ['specific', 'vague', 'insufficient']:
        raise ValueError('Choose evidence specificity.')
    with path.with_suffix('.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        packet, current = load_packet(path)
        if current != revision:
            raise ValueError('The packet changed in another session. Reload before saving.')
        matches = [r for r in packet['reviews'] if r['review_id'] == review_id]
        if len(matches) != 1:
            raise ValueError('Review assignment is missing or duplicated.')
        matches[0].update({k:v.strip() for k,v in values.items()})
        matches[0].update(review_status='completed', reviewed_at=datetime.now(timezone.utc).isoformat(),
                          reviewer_type='user_entered')
        name = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as handle:
                name = handle.name
                json.dump(packet, handle, indent=2)
                handle.write('\n')
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(name, path)
            name = None
        finally:
            if name is not None:
                os.unlink(name)
