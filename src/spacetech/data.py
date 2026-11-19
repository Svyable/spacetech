"""Strict INTERMAGNET IAGA-2002 XYZ parser and minute-gap preservation.

Only XYZ vector files are accepted. HDZ / declination data require a
different unit conversion and are intentionally rejected.
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import numpy as np


def load_iaga2002_xyz(path):
    """Return (UTC datetimes, N x 3 floats in nT), retaining missing minutes.

    Strictly expects DATE TIME DOY and station-prefixed X,Y,Z columns.
    Ignores total scalar F. No network access or bundled third-party data.
    """
    lines = Path(path).read_text(encoding="utf-8-sig").splitlines()
    columns = None
    records = []
    for line in lines:
        parts = line.strip().split()
        if not parts or line.lstrip().startswith("#"):
            continue
        if len(parts) >= 6 and [p.upper() for p in parts[:3]] == ["DATE", "TIME", "DOY"]:
            columns = [p.upper() for p in parts]
            continue
        if columns is None or len(parts) < len(columns):
            continue
        try:
            stamp = datetime.fromisoformat(parts[0] + "T" + parts[1].replace("Z", "+00:00"))
        except ValueError:
            continue
        stamp = stamp.replace(tzinfo=timezone.utc) if stamp.tzinfo is None else stamp.astimezone(timezone.utc)
        if stamp.second or stamp.microsecond:
            raise ValueError("expected minute-aligned IAGA-2002 input")
        channels = {}
        for axis in "XYZ":
            choices = [i for i, name in enumerate(columns[3:], 3) if name.endswith(axis)]
            if len(choices) != 1:
                raise ValueError("only unambiguous XYZ IAGA-2002 vectors are supported")
            channels[axis] = choices[0]
        vector = np.array([float(parts[channels[k]]) for k in "XYZ"])
        # IAGA missing data convention uses large sentinels (e.g., 99999.00).
        if np.any(~np.isfinite(vector)) or np.any(np.abs(vector) >= 88888):
            vector[:] = np.nan
        records.append((stamp, vector))
    if not records:
        raise ValueError("no IAGA-2002 XYZ records found")
    records.sort(key=lambda item: item[0])
    if len({item[0] for item in records}) != len(records):
        raise ValueError("duplicate timestamps")
    start, end = records[0][0], records[-1][0]
    total = int((end - start).total_seconds() // 60) + 1
    if total > 2_000_000:
        raise ValueError("input date span exceeds 2 million minutes")
    aligned = np.full((total, 3), np.nan)
    for stamp, vector in records:
        aligned[int((stamp - start).total_seconds() // 60)] = vector
    timestamps = [start + timedelta(minutes=i) for i in range(total)]
    return timestamps, aligned
