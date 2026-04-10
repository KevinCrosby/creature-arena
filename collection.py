"""Party collection management and wild encounters."""
from __future__ import annotations

import random

from creature import Creature
from data import (
    STARTER_CREATURES, ENCOUNTER_TABLES, get_moves_for_types,
)

MAX_PARTY_SIZE = 6


class Collection:
    """Manages the player's party of creatures."""

    def __init__(self, creatures: list[Creature] | None = None, active_index: int = 0):
        self.creatures: list[Creature] = creatures if creatures is not None else []
        self._active_index = min(active_index, max(0, len(self.creatures) - 1))

    @property
    def active_index(self) -> int:
        if not self.creatures:
            return 0
        return min(self._active_index, len(self.creatures) - 1)

    @active_index.setter
    def active_index(self, value: int) -> None:
        self._active_index = value

    def get_active(self) -> Creature | None:
        """Return the currently active creature, or None if party is empty."""
        if not self.creatures:
            return None
        return self.creatures[self.active_index]

    def add_creature(self, creature: Creature) -> bool:
        """Add a creature to the party. Returns False if party is full."""
        if len(self.creatures) >= MAX_PARTY_SIZE:
            return False
        self.creatures.append(creature)
        return True

    def remove_creature(self, index: int) -> Creature | None:
        """Remove creature at index. Returns the removed creature or None."""
        if index < 0 or index >= len(self.creatures):
            return None
        if len(self.creatures) <= 1:
            return None  # Can't remove last creature
        creature = self.creatures.pop(index)
        if self._active_index >= len(self.creatures):
            self._active_index = len(self.creatures) - 1
        return creature

    def swap_active(self, index: int) -> bool:
        """Set a different creature as active. Returns success."""
        if index < 0 or index >= len(self.creatures):
            return False
        self._active_index = index
        return True

    def is_full(self) -> bool:
        return len(self.creatures) >= MAX_PARTY_SIZE

    def heal_all(self) -> None:
        """Heal all creatures to full HP."""
        for creature in self.creatures:
            creature.heal()

    def to_dict(self) -> dict:
        """Serialize the collection."""
        return {
            "creatures": [c.to_dict() for c in self.creatures],
            "active_index": self.active_index,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Collection:
        """Deserialize a collection."""
        creatures = [Creature.from_dict(c) for c in data.get("creatures", [])]
        return cls(creatures=creatures, active_index=data.get("active_index", 0))


def create_starter(template_index: int) -> Creature:
    """Create a creature from a starter template."""
    if template_index < 0 or template_index >= len(STARTER_CREATURES):
        raise ValueError(f"Invalid template index: {template_index}")
    template = STARTER_CREATURES[template_index]
    moves = get_moves_for_types(template["moves"])
    return Creature(
        name=template["name"],
        creature_type=template["creature_type"],
        level=template["level"],
        moves=moves,
    )


def wild_encounter(area: str) -> Creature | None:
    """Generate a random wild creature from the area's encounter table."""
    table = ENCOUNTER_TABLES.get(area)
    if not table:
        return None
    entry = random.choice(table)
    template = STARTER_CREATURES[entry["template"]]
    level = random.randint(entry["min_level"], entry["max_level"])
    moves = get_moves_for_types(template["moves"])
    return Creature(
        name=template["name"],
        creature_type=template["creature_type"],
        level=level,
        moves=moves,
    )


def catch_attempt(creature: Creature) -> bool:
    """Attempt to catch a creature. Lower HP = higher chance."""
    if creature.max_hp <= 0:
        return False
    hp_ratio = creature.hp / creature.max_hp
    # Base 30% chance at full HP, up to 90% at near-zero HP
    catch_rate = 0.9 - (0.6 * hp_ratio)
    return random.random() < catch_rate
