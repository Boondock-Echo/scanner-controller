"""Preset parameter mappings for the band scope command."""

BAND_SCOPE_PRESETS = {
    # Low frequency, high frequency, step size, modulation
    "air": ("00115000", "00135000", 833, "AM"),
    "race": ("00455000", "00465000", 1250, "FM"),
    "marine": ("00156000", "00162000", 2500, "FM"),
    "railroad": ("00159500", "00161500", 1500, "FM"),
    "ham2m": ("00144000", "00148000", 2000, "FM"),
    "ham70cm": ("00415000", "00455000", 1250, "FM"),
    "weather": ("00161975", "00162975", 2500, "FM"),
    "cb": ("00026905", "00027905", 1000, "AM"),
    "frs": ("00460150", "00470150", 1250, "FM"),
    "public_safety": ("00145000", "00165000", 1250, "FM"),
    "mil_air": ("00222500", "00402500", 2500, "AM"),
}
