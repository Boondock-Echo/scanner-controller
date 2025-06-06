"""Tests ensuring the ``--machine`` mode continues to work as expected.

This module verifies that running the application with the ``--machine``
command-line flag results in the correct machine-friendly output and that the
interactive command loop behaves properly.  Because the real application
depends on the external ``serial`` package to communicate with hardware, a
minimal stub of that package is provided here so that ``main.py`` can be
imported in a test environment without requiring serial hardware or the real
package to be installed.
"""

import os
import sys
import types

sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # noqa: E402

# ``pytest`` adds the repository root to ``sys.path`` when run.

# Provide a minimal stub of the ``serial`` package expected by ``main``.
# Only the bits required for import are defined here.
serial_stub = types.ModuleType("serial")
serial_stub.Serial = lambda *a, **k: None
serial_tools_stub = types.ModuleType("serial.tools")
list_ports_stub = types.ModuleType("serial.tools.list_ports")
list_ports_stub.comports = lambda *a, **k: []
serial_tools_stub.list_ports = list_ports_stub
serial_stub.tools = serial_tools_stub
# Register the stubs so ``import serial`` works during tests
sys.modules.setdefault("serial.tools", serial_tools_stub)
sys.modules.setdefault("serial.tools.list_ports", list_ports_stub)
sys.modules.setdefault("serial", serial_stub)

# Ensure backend utilities can be imported without real serial
import utilities.scanner.backend as backend  # noqa: E402

import main  # noqa: E402
from utilities.command.loop import main_loop as original_main_loop  # noqa: E402


def test_main_machine_mode_enabled(capsys, monkeypatch):
    """Run ``main`` with ``--machine`` and confirm startup behaviour.

    The test replaces :func:`main.main_loop` with a dummy function so we can
    detect whether the loop would have been entered without actually running it.
    It then executes ``main.main()`` with arguments that enable machine mode and
    test output.  The captured output must contain the machine-mode banner as
    well as evidence that the loop was invoked.
    """

    def dummy_loop(adapter, ser, commands, command_help, machine_mode):
        print("MAIN_LOOP_CALLED")

    monkeypatch.setattr(main, "main_loop", dummy_loop)
    monkeypatch.setattr(sys, "argv", ["main.py", "--machine", "--test"])

    main.main()

    out = capsys.readouterr().out
    assert "MACHINE_MODE: ENABLED" in out
    assert "STATUS:INFO|MESSAGE:Ready_for_commands" in out
    assert "MAIN_LOOP_CALLED" in out


def test_main_loop_exit_machine_mode(capsys, monkeypatch):
    """Simulate typing ``exit`` in machine mode and verify messages.

    By patching ``input`` we feed a single ``exit`` command to the
    :func:`utilities.command.loop.main_loop` function.  The readline
    initialization is also stubbed out to keep the test environment simple.
    The output should contain the scanner-ready message followed by the exit
    notification in machine-readable form.
    """
    inputs = ["exit"]

    def fake_input(prompt=""):
        return inputs.pop(0)

    monkeypatch.setattr("builtins.input", fake_input)
    monkeypatch.setattr(
        "utilities.command.loop.initialize_readline", lambda c: None
    )

    original_main_loop(None, None, {}, {}, True)

    out = capsys.readouterr().out
    assert "STATUS:INFO|MESSAGE:Scanner_ready" in out
    assert "STATUS:INFO|ACTION:EXIT" in out
