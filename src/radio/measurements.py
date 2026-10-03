"""Strict, bounded CSV import; no assumptions about instrument accuracy."""
import csv
from pathlib import Path
from .calculations import positive


def read_sweep(path):
    path = Path(path)
    if path.stat().st_size > 5_000_000:
        raise ValueError('CSV is limited to 5 MB.')
    points = []
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if not {'frequency_mhz', 'swr'} <= set(reader.fieldnames or []):
            raise ValueError('CSV needs frequency_mhz and swr columns.')
        for line, row in enumerate(reader, 2):
            if len(points) >= 10000:
                raise ValueError('CSV is limited to 10,000 measurements.')
            try:
                frequency, swr = positive(row['frequency_mhz']), positive(row['swr'])
                if swr < 1:
                    raise ValueError('SWR must be at least 1.')
            except (ValueError, TypeError) as error:
                raise ValueError(f'Line {line}: {error}') from error
            points.append((frequency, swr))
    if not points:
        raise ValueError('CSV has no measurements.')
    return sorted(points)
