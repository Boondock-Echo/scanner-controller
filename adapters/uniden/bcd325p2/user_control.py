"""
User control functions for the BCD325P2 scanner.

Contains functions for simulating key presses and user interactions.
"""


def send_key(self, ser, key_seq):
    """Simulate key presses on the BCD325P2.

    Args:
        ser: Serial connection to the scanner.
        key_seq: Sequence of keys to press.

    Returns:
        str: Combined response from all key presses.
    """
    if not key_seq:
        return self.feedback(False, "No key(s) provided.")

    responses = []
    for char in key_seq:
        if char not in "0123456789<>^.EMFHSLP":
            responses.append(f"{char} → skipped (invalid key)")
            continue
        try:
            response = self.send_command(ser, f"KEY,{char}")
            responses.append(f"{char} → {response}")
        except Exception as e:
            responses.append(f"{char} → ERROR: {e}")
    return "\n".join(responses)
