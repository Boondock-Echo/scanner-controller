"""Close Call operations for the BCD325P2 scanner."""


def get_close_call(self, ser):
    """Return the current Close Call settings."""
    return self.send_command(ser, "CLC")


def set_close_call(self, ser, params):
    """Set Close Call parameters.

    ``params`` may be a string or a sequence of values which will be joined
    with commas.
    """
    if isinstance(params, (list, tuple)):
        params = ",".join(str(p) for p in params)
    return self.send_command(ser, f"CLC,{params}")


def jump_mode(self, ser, jump_mode, index=""):
    """Jump to a specific mode using the JPM command."""
    return self.send_command(ser, f"JPM,{jump_mode},{index}")


def jump_to_number_tag(self, ser, sys_tag="", chan_tag=""):
    """Jump to a system/channel number tag using the JNT command."""
    return self.send_command(ser, f"JNT,{sys_tag},{chan_tag}")

