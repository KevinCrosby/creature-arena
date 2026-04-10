"""Creature trading via shareable codes."""
from __future__ import annotations

import base64
import json
import zlib

from creature import Creature

_PREFIX = "CA1-"


def export_creature(creature: Creature) -> str:
    """Serialize a creature into a compact, shareable trade code."""
    payload = json.dumps(creature.to_dict(), separators=(",", ":")).encode()
    compressed = zlib.compress(payload)
    encoded = base64.urlsafe_b64encode(compressed).decode()
    return f"{_PREFIX}{encoded}"


def import_creature(code: str) -> Creature | None:
    """Reconstruct a creature from a trade code. Returns None on any error."""
    try:
        if not code.startswith(_PREFIX):
            return None
        encoded = code[len(_PREFIX):]
        compressed = base64.urlsafe_b64decode(encoded)
        payload = zlib.decompress(compressed)
        data = json.loads(payload)
        return Creature.from_dict(data)
    except Exception:
        return None


def validate_trade_code(code: str) -> bool:
    """Return True if the code can be successfully imported."""
    return import_creature(code) is not None


def get_trade_summary(code: str) -> str | None:
    """Return a human-readable summary of the creature in a trade code."""
    creature = import_creature(code)
    if creature is None:
        return None
    move_count = len(creature.moves)
    return (
        f"📦 {creature.name} ({creature.creature_type}, "
        f"Lv.{creature.level}, {move_count} move{'s' if move_count != 1 else ''})"
    )
