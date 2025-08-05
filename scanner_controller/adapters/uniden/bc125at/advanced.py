"""
Advanced operations for the BC125AT scanner.

Contains functions for memory operations and other advanced features.
"""

import sys

from scanner_controller.adapters.uniden.common.core import ensure_str


def hex32(value):
    """Convert an integer to a 32-bit hexadecimal string."""
    return f"{value:08X}"


def update_progress(current, total, machine_mode=False):
    """Display a progress bar for long-running operations."""
    percent = int(100 * current / total)

    if machine_mode:
        # Only output progress updates at meaningful intervals to avoid flooding
        if percent % 10 == 0 or percent == 100:
            print(
                f"STATUS:PROGRESS|PERCENT:{percent}|CURRENT:{current}|"
                f"TOTAL:{total}"
            )
    else:
        bar = "#" * (percent // 2)
        sys.stdout.write(f"\rProgress: [{bar:<50}] {percent}%")
        sys.stdout.flush()
        if current == total:
            sys.stdout.write("\n")
            sys.stdout.flush()


def dump_memory_to_file(
    self,
    ser,
    filename="memorydump.txt",
    start=0x00010000,
    end=0x0001FFFF,
    step=16,
):
    """Dump scanner memory to a file.

    Args:
        ser: Serial connection to the scanner.
        filename: Output filename.
        start: Starting memory address.
        end: Ending memory address.
        step: Memory chunk size.

    Returns:
        str: Status message after dump attempt.
    """
    try:
        self.enter_programming_mode(ser)
        total_steps = ((end - start) // step) + 1
        valid_count, invalid_streak = 0, 0
        MAX_INVALID = 4096
        with open(filename, "w") as f:
            for i in range(total_steps):
                addr = start + i * step
                cmd = f"MRD,{hex32(addr)}"
                response = self.send_command(ser, cmd)
                response_str = ensure_str(response)

                if response_str.startswith("MRD,"):
                    f.write(response_str + "\n")
                    valid_count += 1
                    invalid_streak = 0
                elif "ERR" in response_str or "NG" in response_str:
                    invalid_streak += 1
                else:
                    f.write(f"# Unexpected: {response_str}\n")
                    invalid_streak += 1

                if invalid_streak >= MAX_INVALID:
                    return self.feedback(
                        False, f"Aborted early — {MAX_INVALID} invalids."
                    )
                update_progress(
                    i,
                    total_steps,
                    hasattr(self, "machine_mode") and self.machine_mode,
                )
        self.exit_programming_mode(ser)
        return self.feedback(
            True, f"{valid_count} MRD entries written to {filename}"
        )
    except Exception as e:
        try:
            self.exit_programming_mode(ser)
        except Exception:
            pass
        return self.feedback(False, f"Memory Dump Error: {e}")
