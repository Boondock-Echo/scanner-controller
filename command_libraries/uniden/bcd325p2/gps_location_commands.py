"""
GPS and Location Alert System commands for the BCD325P2.

These commands allow management of location-based alerts and GPS display
options.
"""

from utilities.core.shared_utils import scanner_command
from utilities.validators import validate_param_constraints

GPS_LOCATION_COMMANDS = {
    "GDO": scanner_command(
        name="GDO",
        requires_prg=True,
        set_format=(
            "GDO,{disp_mode},{unit},{time_format},{time_zone},{pos_format}"
        ),
        validator=validate_param_constraints(
            [
                (int, {0, 1, 2, 3, 4}),
                # disp_mode (0:ETA, 1:Clock, 2:Elevation, 3:Speed, 4:Location)
                (int, {0, 1}),  # unit (0:mile, 1:km)
                (int, {0, 1}),  # time_format (0:12H, 1:24H)
                (str, None),  # time_zone (-14.0 to 14.0)
                (str, {"DMS", "DEG"}),  # pos_format (DMS/DEG)
            ]
        ),
        help="""Get/Set GPS Display Options.

        Format:
        GDO - Get current GPS display settings
        GDO,[DISP_MODE],[UNIT],[TIME_FORMAT],[TIME_ZONE],[POS_FORMAT] - Set
        GPS display options

        Parameters:
        DISP_MODE : Display GPS mode (0:ETA, 1:Clock, 2:Elevation, 3:Speed,
        4:Location)
        UNIT : Distance unit (0:mile, 1:km)
        TIME_FORMAT : Time format (0:12H, 1:24H)
        TIME_ZONE : Time zone (-14.0/-13.5/.../-0.5/0.0/0.5/.../13.5/14.0)
        POS_FORMAT : Position format (DMS/DEG)
        """,
    ),
    "LIH": scanner_command(
        name="LIH",
        requires_prg=True,  # This command requires program mode
        set_format="LIH,{las_type}",
        validator=validate_param_constraints(
            [(str, {"POI", "DROAD", "DXING"})]  # Location Alert Type
        ),
        help="""Get Location Alert System Index Head.

        Format:
        LIH,[LAS_TYPE] - Get the first index of stored location alert system
        list

        Parameters:
        LAS_TYPE : Location Alert Type (POI: POI / DROAD: Dangerous Road /
        DXING: Dangerous Xing)

        Returns:
        The first index of stored location alert system list
        """,
    ),
    "LIT": scanner_command(
        name="LIT",
        requires_prg=True,
        set_format="LIT,{las_type}",
        validator=validate_param_constraints(
            [(str, {"POI", "DROAD", "DXING"})]  # Location Alert Type
        ),
        help="""Get Location Alert System Index Tail.

        Format:
        LIT,[LAS_TYPE] - Get the last index of stored location alert system list

        Parameters:
        LAS_TYPE : Location Alert Type (POI: POI / DROAD: Dangerous Road /
        DXING: Dangerous Xing)

        Returns: The last index of stored location alert system list
        """,
    ),
    "CLA": scanner_command(
        name="CLA",
        requires_prg=True,
        set_format="CLA,{las_type}",
        validator=validate_param_constraints(
            [(str, {"POI", "DROAD", "DXING"})]  # Location Alert Type
        ),
        help="""Create Location Alert System.

        Format:
        CLA,[LAS_TYPE] - Create a location alert system

        Parameters:
        LAS_TYPE : Location Alert Type (POI: POI / DROAD: Dangerous Road /
        DXING: Dangerous Xing)

        Returns:
        Location Alert System Index or -1 if failed
        """,
    ),
    "DLA": scanner_command(
        name="DLA",
        requires_prg=True,
        set_format="DLA,{index}",
        validator=validate_param_constraints([(int, None)]),  # index
        help="""Delete Location Alert System.

        Format:
        DLA,[INDEX] - Delete a location alert system

        Parameters:
        INDEX : Location Alert System Index
        """,
    ),
    "LIN": scanner_command(
        name="LIN",
        requires_prg=True,
        set_format=(
            "LIN,{index},{las_type},{name},{lout},{alt},{altl},{latitude},"
            "{longitude},{range},{speed},{dir},{alt_color},{alt_pattern}"
        ),
        validator=validate_param_constraints(
            [
                (int, None),  # index
                (str, {"POI", "DROAD", "DXING"}),  # Location Alert Type
                (str, lambda x: len(x) <= 16),  # name (max 16 chars)
                (int, {0, 1}),  # lout (0: Unlocked, 1: Lockout)
                (
                    int,
                    lambda x: x == 0 or 1 <= x <= 4,
                ),  # alt (0: OFF, 1-4: Tone No.)
                (int, lambda x: x == 0 or 1 <= x <= 15),  # altl (0: AUTO, 1-15)
                (str, None),  # latitude
                (str, None),  # longitude
                (int, (1, 80)),  # range (1-80: 1=0.05 mile or km)
                (int, (0, 200)),  # speed (0-200 mph or km/h)
                (
                    int,
                    {0, 44, 90, 134, 180, 224, 270, 314, 360},
                ),  # dir (heading)
                (str, {"OFF", "RED"}),  # alt_color
                (int, {0, 1, 2}),  # alt_pattern (0: ON, 1: Slow, 2: Fast)
            ]
        ),
        help="""Get/Set Location Alert System Info.

        Format:
        LIN,[INDEX] - Get location alert system information
        LIN,[INDEX],[LAS_TYPE],[NAME],[LOUT],[ALT],[ALTL],[LATITUDE],
        [LONGITUDE],[RANGE],[SPEED],[DIR],[ALT_COLOR],[ALT_PATTERN]

        Parameters:
        INDEX : Location Alert System Index
        LAS_TYPE : Location Alert Type (POI, DROAD, DXING)
        NAME : Name (max 16 chars)
        LOUT : Lockout (0: Unlocked, 1: Lockout)
        ALT : Alert Tone (0: OFF, 1-4: Tone No.)
        ALTL : Alert Tone Level (0: AUTO, 1-15)
        LATITUDE : North or South Latitude (in DMS or DEG format based on GPS
        settings)
        LONGITUDE : West or East Longitude (in DMS or DEG format based on GPS
        settings)
        RANGE : Range (1-80: 1=0.05 mile or km)
        SPEED : Speed Limit (0-200: mph or km/h)
        DIR : Heading (360: All range, 0: North, 44: NE, 90: East, 134: SE,
        180: South, 224: SW, 270: West, 314: NW)
        ALT_COLOR : Alert Light color (OFF, RED)
        ALT_PATTERN : Alert Light Pattern (0: ON, 1: Slow, 2: Fast)
        """,
    ),
}

# Set source module for each command
for cmd in GPS_LOCATION_COMMANDS.values():
    cmd.source_module = "GPS_LOCATION_COMMANDS"
