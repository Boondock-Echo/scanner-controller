"""
This module is part of the Universal Scanner Controller project.

It provides tone lookup tables (LUT) for CTCSS and DCS tones used in Uniden
scanners. The module includes mappings for tone codes to frequencies and reverse
mappings for frequencies to tone codes. It also provides validation functions
for CTCSS and DCS inputs.
"""

# print(DCS_LOOKUP[128])  # ➜ "DCS023"
# print(DCS_REVERSE_LOOKUP["DCS023"])  # ➜ 128


def validate_ctcss(value):
    """
    Validate and normalize CTCSS input.

    Accepts: integer code, float/string frequency like "67.0Hz" or "67.0"
    Returns: valid integer CTCSS code, or raises ValueError
    """
    if isinstance(value, int):
        if value in CTCSS_LUT:
            return value
        raise ValueError(f"Invalid CTCSS code: {value}")

    if isinstance(value, float):
        value = f"{value:.1f}Hz"
    elif isinstance(value, str):
        value = value.strip().upper().replace(" HZ", "HZ")
        if not value.endswith("HZ"):
            value += "HZ"

    if value in CTCSS_reverse_LUT:
        return CTCSS_reverse_LUT[value]
    raise ValueError(f"Invalid CTCSS frequency: {value}")


def validate_dcs(value):
    """
    Validate and normalize DCS input.

    Accepts: integer code, string like "DCS 023" or "023"
    Returns: valid integer DCS code, or raises ValueError
    """
    if isinstance(value, int):
        if value in DCS_LUT:
            return value
        raise ValueError(f"Invalid DCS code: {value}")

    value = str(value).strip().upper()
    if not value.startswith("DCS"):
        value = f"DCS{value.zfill(3)}"

    if value in DCS_reverse_LUT:
        return DCS_reverse_LUT[value]
    raise ValueError(f"Invalid DCS label: {value}")


CTCSS_LUT = {
    64: "67.0Hz",
    65: "69.3Hz",
    66: "71.9Hz",
    67: "74.4Hz",
    68: "77.0Hz",
    69: "79.7Hz",
    70: "82.5Hz",
    71: "85.4Hz",
    72: "88.5Hz",
    73: "91.5Hz",
    74: "94.8Hz",
    75: "97.4Hz",
    76: "100.0Hz",
    77: "103.5Hz",
    78: "107.2Hz",
    79: "110.9Hz",
    80: "114.8Hz",
    81: "118.8Hz",
    82: "123.0Hz",
    83: "127.3Hz",
    84: "131.8Hz",
    85: "136.5Hz",
    86: "141.3Hz",
    87: "146.2Hz",
    88: "151.4Hz",
    89: "156.7Hz",
    90: "159.8Hz",
    91: "162.2Hz",
    92: "165.5Hz",
    93: "167.9Hz",
    94: "171.3Hz",
    95: "173.8Hz",
    96: "177.3Hz",
    97: "179.9Hz",
    98: "183.5Hz",
    99: "186.2Hz",
    100: "189.9Hz",
    101: "192.8Hz",
    102: "196.6Hz",
    103: "199.5Hz",
    104: "203.5Hz",
    105: "206.5Hz",
    106: "210.7Hz",
    107: "218.1Hz",
    108: "225.7Hz",
    109: "229.1Hz",
    110: "233.6Hz",
    111: "241.8Hz",
    112: "250.3Hz",
    113: "254.1Hz",
    127: "SEARCH",
    0: "NONE / All",
}

DCS_LUT = {
    128: "DCS023",
    129: "DCS025",
    130: "DCS026",
    131: "DCS031",
    132: "DCS032",
    133: "DCS036",
    134: "DCS043",
    135: "DCS047",
    136: "DCS051",
    137: "DCS053",
    138: "DCS054",
    139: "DCS065",
    140: "DCS071",
    141: "DCS072",
    142: "DCS073",
    143: "DCS074",
    144: "DCS114",
    145: "DCS115",
    146: "DCS116",
    147: "DCS122",
    148: "DCS125",
    149: "DCS131",
    150: "DCS132",
    151: "DCS143",
    152: "DCS145",
    153: "DCS152",
    154: "DCS155",
    155: "DCS156",
    156: "DCS162",
    157: "DCS165",
    158: "DCS172",
    159: "DCS174",
    160: "DCS205",
    161: "DCS223",
    162: "DCS212",
    163: "DCS223",
    164: "DCS225",
    165: "DCS226",
    166: "DCS243",
    167: "DCS244",
    168: "DCS245",
    169: "DCS246",
    170: "DCS251",
    171: "DCS252",
    172: "DCS255",
    173: "DCS261",
    174: "DCS263",
    175: "DCS265",
    176: "DCS266",
    177: "DCS274",
    178: "DCS306",
    179: "DCS311",
    180: "DCS315",
    181: "DCS325",
    182: "DCS331",
    183: "DCS343",
    184: "DCS346",
    185: "DCS351",
    186: "DCS364",
    187: "DCS365",
    188: "DCS371",
    189: "DCS411",
    190: "DCS412",
    191: "DCS413",
    192: "DCS423",
    193: "DCS431",
    194: "DCS432",
    195: "DCS445",
    196: "DCS446",
    197: "DCS452",
    198: "DCS454",
    199: "DCS462",
    200: "DCS464",
    201: "DCS465",
    202: "DCS466",
    203: "DCS503",
    204: "DCS506",
    205: "DCS516",
    206: "DCS523",
    207: "DCS526",
    208: "DCS532",
    209: "DCS546",
    210: "DCS565",
    211: "DCS606",
    212: "DCS612",
    213: "DCS624",
    214: "DCS627",
    215: "DCS631",
    216: "DCS632",
    217: "DCS654",
    218: "DCS662",
    219: "DCS664",
    220: "DCS703",
    221: "DCS712",
    222: "DCS723",
    223: "DCS731",
    224: "DCS732",
    225: "DCS734",
    226: "DCS743",
    227: "DCS250",
    228: "DCS007",
    229: "DCS015",
}

# Reverse lookup tables
CTCSS_reverse_LUT = {v: k for k, v in CTCSS_LUT.items()}
DCS_reverse_LUT = {v: k for k, v in DCS_LUT.items()}
