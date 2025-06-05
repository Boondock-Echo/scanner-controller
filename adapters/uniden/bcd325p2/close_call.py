"""Close Call helper functions for the BCD325P2 scanner."""


def get_close_call(self, ser):
    """Return current Close Call settings (raw CLC response)."""
    return self.send_command(ser, "CLC")


def set_close_call(self, ser, params):
    """Set Close Call parameters using ``CLC`` command."""
    if isinstance(params, (list, tuple)):
        params = ",".join(str(x) for x in params)
    return self.send_command(ser, f"CLC,{params}")


def jump_mode(self, ser, jump_mode, index=""):
    """Jump to the specified mode and index."""
    return self.send_command(ser, f"JPM,{jump_mode},{index}")


def jump_to_number_tag(self, ser, sys_tag="", chan_tag=""):
    """Jump to a system and channel number tag."""
    return self.send_command(ser, f"JNT,{sys_tag},{chan_tag}")
