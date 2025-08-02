"""Simple tests for band scope logger."""

from utilities.scanner.band_scope_logger import record_band_scope


def test_record_band_scope_csv(tmp_path):
    """Verify CSV logging."""
    outfile = tmp_path / "out.csv"
    records = [(100.0, 0.5), (101.0, 0.6)]
    result = record_band_scope(records, "summary", "csv", str(outfile))
    assert result == str(outfile)
    assert outfile.exists()
