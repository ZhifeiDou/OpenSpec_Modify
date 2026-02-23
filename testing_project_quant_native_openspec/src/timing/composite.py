"""Composite timing signal combining all individual signals."""


def composite_timing_signal(signals: list[dict], enabled: bool = True) -> dict:
    """Combine individual timing signals into composite multiplier.

    Args:
        signals: List of signal dicts, each with 'signal' and 'multiplier'.
        enabled: Whether timing is enabled. If False, returns 1.0.

    Returns:
        dict with 'multiplier' (product of all) and 'signals' (list of signal names).
    """
    if not enabled:
        return {"multiplier": 1.0, "signals": ["timing_disabled"]}

    multiplier = 1.0
    signal_names = []

    for sig in signals:
        multiplier *= sig.get("multiplier", 1.0)
        signal_names.append(sig.get("signal", "unknown"))

    return {
        "multiplier": multiplier,
        "signals": signal_names,
    }
