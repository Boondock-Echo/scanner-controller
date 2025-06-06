"""Preset parameter mappings for the band scope command."""

BAND_SCOPE_PRESETS = {
    # Center frequency, step size, span, max hold flag
    "air": ("00125000", 833, "20M", 0),
    "race": ("00460000", 1250, "10M", 0),
    "marine": ("00159000", 2500, "6M", 0),
    "railroad": ("00160500", 1500, "2M", 0),
    "ham2m": ("00146000", 2000, "4M", 0),
    "ham70cm": ("00435000", 1250, "40M", 0),
    "weather": ("00162475", 2500, "1M", 0),
    "cb": ("00027405", 1000, "1M", 0),
    "frs": ("00465150", 1250, "10M", 0),
    "public_safety": ("00155000", 1250, "20M", 0),
    "mil_air": ("00312500", 2500, "180M", 0),
}
