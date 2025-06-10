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


def render_band_scope_waterfall(pairs, width=64):
    """Render band scope results as a waterfall-style graph.

    Parameters
    ----------
    pairs : list of tuple
        ``(frequency, rssi)`` tuples with RSSI normalized between ``0`` and ``1``.
    width : int, optional
        Number of frequency bins to divide the data into. Defaults to ``64``.

    Returns
    -------
    str
        Multiple lines of characters where each line represents one sweep.
    """

    if not pairs or width <= 0:
        return ""

    freqs = [f for f, _ in pairs]
    f_min = min(freqs)
    f_max = max(freqs)
    if f_max == f_min:
        f_max += 1e-6
    bin_size = (f_max - f_min) / float(width)

    rows = []
    bins = [[0.0, 0] for _ in range(width)]
    prev_freq = None

    for freq, rssi in pairs:
        if prev_freq is not None and freq < prev_freq:
            rows.append(bins)
            bins = [[0.0, 0] for _ in range(width)]
        prev_freq = freq
        idx = int((freq - f_min) / bin_size)
        if idx >= width:
            idx = width - 1
        if rssi is not None:
            bins[idx][0] += rssi
            bins[idx][1] += 1

    rows.append(bins)

    lines = []
    max_level = len(BLOCKS) - 1
    for row in rows:
        chars = []
        for total, count in row:
            if count == 0:
                level = 0
            else:
                avg = total / count
                level = max(0, min(max_level, int(round(avg * max_level))))
            chars.append(BLOCKS[level])
        lines.append("".join(chars))

    return "\n".join(lines)


def split_output_lines(output, width):
    """Wrap each line of ``output`` so no line exceeds ``width`` characters."""

    if width <= 0:
        return output

    wrapped_lines = []
    for line in output.splitlines():
        while len(line) > width:
            wrapped_lines.append(line[:width])
            line = line[width:]
        wrapped_lines.append(line)

    return "\n".join(wrapped_lines)


