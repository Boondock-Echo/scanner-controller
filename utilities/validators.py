"""
Validators module.

This module provides validation functions for scanner commands and parameters.
These validators ensure that command parameters meet the required format and
value constraints before being sent to the scanner, preventing errors and
improving reliability.
"""


def validate_enum(name, allowed_values):
    """
    Create a validator function that checks if a value is in an allowed set.

    Args:
        name (str): Name of the parameter being validated
            (used in error messages)
        allowed_values (list): List of allowed values for the parameter

    Returns:
        function: A validator function that raises ValueError if the input is
            invalid

    Example:
        >>> validate_mode = validate_enum("MODE", ["AUTO", "AM", "FM", "NFM"])
        >>> validate_mode("FM")  # No error
        >>> validate_mode("LSB")  # Raises ValueError
    """
    allowed_upper = {v.upper() for v in allowed_values}

    def validator(value):
        """
        Validate that a value is in the allowed set (case-insensitive).

        Args:
            value: The value to validate

        Raises:
            ValueError: If the value is not in the allowed set
        """
        if str(value).upper() not in allowed_upper:
            raise ValueError(
                f"{name} must be one of: {', '.join(sorted(allowed_upper))}"
            )

    return validator


def validate_cin(params):
    """
    Validate the argument list for the CIN command.

    Args:
        params (str or list): Should be a comma-separated string or
            list of values.

    Raises:
        ValueError: If the format or fields are invalid

    Returns:
        The validated params (unchanged if valid)
    """
    if isinstance(params, str):
        parts = [p.strip() for p in params.split(",")]
    else:
        parts = list(params)

    if len(parts) not in {1, 9}:
        raise ValueError("CIN requires 1 (read) or 9 (write) arguments")

    index = int(parts[0])
    if not (1 <= index <= 500):
        raise ValueError("Index must be between 1 and 500")

    if len(parts) == 9:
        name = parts[1]
        freq = int(parts[2])
        mod = parts[3].upper()
        ctcss = int(parts[4])
        delay = int(parts[5])
        lockout = int(parts[6])
        priority = int(parts[7])

        if len(name) > 16:
            raise ValueError("Name must be 16 characters or fewer")

        if not (10000 <= freq <= 1300000):
            raise ValueError("Frequency seems invalid (check units?)")

        if mod not in {"AUTO", "AM", "FM", "NFM"}:
            raise ValueError("Modulation must be AUTO, AM, FM, or NFM")

        if not (0 <= ctcss <= 231):
            raise ValueError("CTCSS/DCS code must be 0–231")

        if delay not in {-10, -5, 0, 1, 2, 3, 4, 5}:
            raise ValueError("Delay must be one of: -10, -5, 0–5")

        if lockout not in {0, 1}:
            raise ValueError("Lockout must be 0 or 1")

        if priority not in {0, 1}:
            raise ValueError("Priority must be 0 or 1")
    return params
