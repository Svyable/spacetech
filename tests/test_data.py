from datetime import timezone
import numpy as np
import pytest

from spacetech.data import load_iaga2002_xyz


def test_iaga_xyz_and_missing_minutes(tmp_path):
    path = tmp_path / "sample.min"
    path.write_text(chr(10).join([
        " Format                 IAGA-2002",
        " IAGA CODE              AAA",
        " Reported               XYZF",
        "DATE TIME DOY AAAX AAAY AAAZ AAAF",
        "2024-05-10 00:00:00.000 131 12000 500 42000 44000",
        "2024-05-10 00:01:00.000 131 12001 499 42001 44000",
        "2024-05-10 00:03:00.000 131 99999 99999 99999 99999",
        "",
    ]))
    times, values = load_iaga2002_xyz(path)
    assert values.shape == (4, 3)
    assert times[0].tzinfo == timezone.utc
    np.testing.assert_array_equal(values[1], [12001, 499, 42001])
    assert np.isnan(values[2:]).all()


def test_rejects_unconverted_hdz_data(tmp_path):
    path = tmp_path / "hdz.min"
    path.write_text(chr(10).join([
        "DATE TIME DOY AAAH AAAD AAAZ AAAF",
        "2024-05-10 00:00:00.000 131 10000 100 40000 41000",
    ]))
    with pytest.raises(ValueError, match="XYZ"):
        load_iaga2002_xyz(path)


def test_duplicate_timestamps_rejected(tmp_path):
    path = tmp_path / "dups.min"
    path.write_text(chr(10).join([
        "DATE TIME DOY AAAX AAAY AAAZ AAAF",
        "2024-05-10 00:00:00.000 131 1 2 3 4",
        "2024-05-10 00:00:00.000 131 5 6 7 8",
    ]))
    with pytest.raises(ValueError, match="duplicate"):
        load_iaga2002_xyz(path)
