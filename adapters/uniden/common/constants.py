"""Common constants for Uniden scanner adapters."""

# Number of Hertz in one megahertz
HZ_PER_MHZ = 1_000_000

# Number of Hertz represented by a single scanner unit
HZ_PER_SCANNER_UNIT = 100

# Number of scanner units in one megahertz
SCANNER_UNITS_PER_MHZ = HZ_PER_MHZ // HZ_PER_SCANNER_UNIT

__all__ = ["HZ_PER_MHZ", "HZ_PER_SCANNER_UNIT", "SCANNER_UNITS_PER_MHZ"]
