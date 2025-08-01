"""
User control functions for the BC125AT scanner.

Contains functions for simulating key presses and user interactions.
"""


def send_key(self, ser, key_seq):
    """Simulate key presses on the BC125AT.

    Args:
        ser: Serial connection to the scanner.
        key_seq: Sequence of keys to press.

    Returns:
        str: Combined response from all key presses.
    """
    if not key_seq:
        return self.feedback(False, "No key(s) provided.")

    success = True
    responses = []
    for char in key_seq:
        if char not in "0123456789<>^.EMFHSLP":
            responses.append(f"{char} → skipped (invalid key)")
            success = False
            continue
        try:
            response = self.send_command(
                ser, f"KEY,{char}"
            )  # Remove the ,P parameter
            responses.append(f"{char} → {response}")
        except Exception as e:
            responses.append(f"{char} → ERROR: {e}")
            success = False

    return self.feedback(success, "\n".join(responses))


def start_scanning(self, ser):
    """Resume scanning mode."""
    return self.send_key(ser, "S")


def stop_scanning(self, ser):
    """Hold on current channel/frequency."""
    return self.send_key(ser, "H")
