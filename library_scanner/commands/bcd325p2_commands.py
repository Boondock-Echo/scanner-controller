from utilities.shared_utils import scanner_command

commands = {
    "VOL": scanner_command(
        name="VOL",
        valid_range=(0, 15),
        help="Set volume level (0-15)."
    ),
    "CLC": scanner_command(
        name="CLC",
        requires_prg=True,
        help="Configure Close Call mode (priority, override, alert tones, etc.)"
    ),
    # ...existing commands...
}
