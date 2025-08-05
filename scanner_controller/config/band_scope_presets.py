"""Preset parameter mappings for the band scope command."""

BAND_SCOPE_PRESETS = {
    # Low frequency, high frequency, step size, modulation
    "air": ("01080000", "01360000", 833, "AM"),
    "race": ("04550000", "04650000", 1250, "FM"),
    "marine": ("01560000", "01620000", 2500, "FM"),
    "railroad": ("01595000", "01615000", 1500, "FM"),
    "ham2m": ("01440000", "01480000", 2000, "FM"),
    "ham70cm": ("04200000", "04500000", 1250, "FM"),
    "weather": ("01624000", "01625500", 2500, "FM"),
    "cb": ("00269650", "00274050", 1000, "AM"),
    "frs": ("04625625", "04677125", 1250, "FM"),
    "public_safety": ("01500000", "01740000", 1250, "FM"),
    "mil_air": ("02250000", "04000000", 2500, "AM"),
}
