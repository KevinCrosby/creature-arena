"""JSON save/load with schema versioning and validation."""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

from collection import Collection
from creature import Creature

SCHEMA_VERSION = 1
DEFAULT_SAVE_DIR = os.path.expanduser("~/.creature-arena")
DEFAULT_SAVE_PATH = os.path.join(DEFAULT_SAVE_DIR, "save.json")


def save_game(collection: Collection, path: str = DEFAULT_SAVE_PATH) -> bool:
    """Save the collection to a JSON file. Returns True on success."""
    try:
        save_dir = os.path.dirname(path)
        os.makedirs(save_dir, exist_ok=True)
        data = {
            "schema_version": SCHEMA_VERSION,
            "saved_at": datetime.now().isoformat(),
            "collection": collection.to_dict(),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except (OSError, TypeError) as e:
        print(f"Warning: Could not save game: {e}")
        return False


def load_game(path: str = DEFAULT_SAVE_PATH) -> Collection | None:
    """Load a collection from a JSON file. Returns None on failure."""
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Warning: Could not load save file: {e}")
        return None

    # Validate schema version
    version = data.get("schema_version")
    if version is None:
        print("Warning: Save file missing schema version, skipping.")
        return None
    if version > SCHEMA_VERSION:
        print(f"Warning: Save file version {version} is newer than supported ({SCHEMA_VERSION}).")
        return None

    # Validate collection data
    collection_data = data.get("collection")
    if not isinstance(collection_data, dict):
        print("Warning: Save file missing or invalid collection data.")
        return None

    try:
        collection = Collection.from_dict(collection_data)
    except (KeyError, TypeError, ValueError) as e:
        print(f"Warning: Could not parse save data: {e}")
        return None

    # Validate each creature
    for creature in collection.creatures:
        if not validate_creature(creature):
            print(f"Warning: Creature '{creature.name}' has invalid stats, repairing.")
            _repair_creature(creature)

    return collection


def validate_creature(creature: Creature) -> bool:
    """Check that a creature's stats are within valid bounds."""
    if creature.level < 1:
        return False
    expected_max_hp = 20 + (creature.level * 5)
    if creature.max_hp != expected_max_hp:
        return False
    if creature.hp < 0 or creature.hp > creature.max_hp:
        return False
    if creature.creature_type not in ("fire", "water", "nature", "electric", "shadow"):
        return False
    return True


def _repair_creature(creature: Creature) -> None:
    """Fix a creature's stats to match its level."""
    creature.level = max(1, creature.level)
    creature.max_hp = 20 + (creature.level * 5)
    creature.hp = max(0, min(creature.hp, creature.max_hp))
    creature.attack = 5 + (creature.level * 2)
    creature.defense = 3 + creature.level
    creature.xp_to_next = creature.level * 10


def delete_save(path: str = DEFAULT_SAVE_PATH) -> bool:
    """Delete a save file. Returns True if deleted."""
    try:
        if os.path.exists(path):
            os.remove(path)
            return True
        return False
    except OSError:
        return False
