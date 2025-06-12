"""Preset parameter mappings for the band scope command."""

BAND_SCOPE_PRESETS = {
    # Low frequency, high frequency, step size, modulation
    "air": ("01150000", "01350000", 833, "AM"),
    "race": ("04550000", "04650000", 1250, "FM"),
    "marine": ("01560000", "01620000", 2500, "FM"),
    "railroad": ("01595000", "01615000", 1500, "FM"),
    "ham2m": ("01440000", "01480000", 2000, "FM"),
    "ham70cm": ("04150000", "04550000", 1250, "FM"),
    "weather": ("01619750", "01629750", 2500, "FM"),
    "cb": ("00269050", "00279050", 1000, "AM"),
    "frs": ("04601500", "04701500", 1250, "FM"),
    "public_safety": ("01450000", "01650000", 1250, "FM"),
    "mil_air": ("02225000", "04025000", 2500, "AM"),
}
