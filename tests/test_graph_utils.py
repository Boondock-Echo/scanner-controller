import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utilities.graph_utils import render_rssi_graph


def test_render_rssi_graph_levels():
    data = [(0, x / 15.0) for x in range(16)]
    output = render_rssi_graph(data)
    lines = output.splitlines()
    assert len(lines) == 2
    assert len(lines[0]) == 16
    assert len(lines[1]) == 16


