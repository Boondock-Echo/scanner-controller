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
        return value

    return validator


def validate_param_constraints(param_constraints):
    """
    Create a validator function based on parameter constraints.

    Args:
        param_constraints (list): List of (type, constraint) tuples
            where 'type' is a Python type (int, str, etc.)
            and 'constraint' can be:
                - None (no constraint)
                - tuple(min, max) for numeric ranges
                - set of allowed values
                - callable validator function

    Returns:
        function: A validator function for command parameters
    """

    def validator(params):
        if isinstance(params, str):
            parts = [p.strip() for p in params.split(",")]
        else:
            parts = list(params)

        if len(parts) != len(param_constraints):
            raise ValueError(
                f"Expected {len(param_constraints)} parameters,"
                f" got {len(parts)}"
            )

        for i, (value, (param_type, constraint)) in enumerate(
            zip(parts, param_constraints)
        ):
            # Validate type
            try:
                typed_value = param_type(value)
                parts[i] = typed_value  # Update with typed value
            except ValueError:
                raise ValueError(
                    f"Parameter {i+1} should be a valid {param_type.__name__}"
                )

            # Validate constraints
            if constraint is None:
                continue
            elif isinstance(constraint, tuple) and len(constraint) == 2:
                min_val, max_val = constraint
                if not (min_val <= typed_value <= max_val):
                    raise ValueError(
                        f"Parameter {i+1} must be between {min_val} and "
                        f"{max_val}"
                    )
            elif isinstance(constraint, set):
                if typed_value not in constraint:
                    raise ValueError(
                        f"Parameter {i+1} must be one of:"
                        f" {', '.join(map(str, sorted(constraint)))}"
                    )
            elif callable(constraint):
                try:
                    constraint(typed_value)
                except ValueError as e:
                    raise ValueError(f"Parameter {i+1}: {str(e)}")

        return params

    return validator


def validate_binary_options(options_count):
    """
    Create a validator for a binary options field (e.g., '01101').

    Args:
        options_count (int): The number of binary digits in the field

    Returns:
        function: A validator function for binary option strings
    """

    def validator(value):
        value = str(value)
        if len(value) != options_count or not all(
            digit in "01" for digit in value
        ):
            raise ValueError(
                f"Value must be a {options_count}-digit binary string"
                f" (e.g., {'0' * options_count})"
            )
        return value

    return validator
