"""Portable JSON experiments with atomic saves."""
import json
import os
import tempfile
from pathlib import Path

FIELDS = ('title', 'date', 'question', 'equipment', 'procedure', 'observations', 'conclusion')


def save_experiment(path, values):
    payload = {'schema_version': 1, **{key: str(values.get(key, '')) for key in FIELDS}}
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as stream:
            temporary = stream.name
            json.dump(payload, stream, indent=2, ensure_ascii=False)
            stream.write('\n')
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def load_experiment(path):
    path = Path(path)
    if path.stat().st_size > 2_000_000:
        raise ValueError('Experiment files are limited to 2 MB.')
    payload = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(payload, dict) or payload.get('schema_version') != 1:
        raise ValueError('Unsupported experiment format.')
    if any(not isinstance(payload.get(key, ''), str) for key in FIELDS):
        raise ValueError('Experiment fields must be text.')
    return {key: payload.get(key, '') for key in FIELDS}
