"""Utilities for visualizing RSSI sweep data."""

BLOCKS = [" ", "\u2581", "\u2582", "\u2583", "\u2584", "\u2585", "\u2586", "\u2587", "\u2588"]


def render_rssi_graph(pairs):
    """Return a two-line unicode graph from ``(freq, rssi)`` pairs.

    Parameters
    ----------
    pairs : list of tuple
        Sequence of ``(frequency, rssi)`` tuples where RSSI is normalized
        between ``0`` and ``1``.

    Returns
    -------
    str
        Two lines of characters representing relative signal strength.
    """
    top = []
    bottom = []
    for _, rssi in pairs:
        if rssi is None:
            level = 0
        else:
            level = max(0, min(16, int(round(rssi * 16))))
        if level <= 8:
            bottom_idx = level
            top_idx = 0
        else:
            bottom_idx = 8
            top_idx = level - 8
        bottom.append(BLOCKS[bottom_idx])
        top.append(BLOCKS[top_idx])
    return "".join(top) + "\n" + "".join(bottom)


