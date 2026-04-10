"""Creature breeding system for producing offspring from compatible parents."""
from __future__ import annotations

import random

from creature import Creature, Move
from data import (
    BREEDING_TABLE,
    CREATURE_ABILITIES,
    DUAL_TYPE_CREATURES,
    MOVE_POOL,
    get_moves_for_types,
)


def can_breed(creature_a: Creature, creature_b: Creature) -> bool:
    """Check whether two creatures are eligible to breed."""
    if creature_a.level < 5 or creature_b.level < 5:
        return False
    if creature_a.is_fainted() or creature_b.is_fainted():
        return False
    if creature_a is creature_b:
        return False
    type_key = tuple(sorted([creature_a.creature_type, creature_b.creature_type]))
    return type_key in BREEDING_TABLE


def get_breeding_result_type(type_a: str, type_b: str) -> tuple[str, str | None]:
    """Determine offspring types from two parent types."""
    sorted_types = tuple(sorted([type_a, type_b]))
    possible = BREEDING_TABLE[sorted_types]
    primary = random.choice(possible)
    secondary: str | None = None
    if type_a != type_b and random.random() < 0.4:
        other = type_b if primary == type_a else type_a
        secondary = other
    return primary, secondary


def breed_creatures(parent_a: Creature, parent_b: Creature) -> Creature | None:
    """Breed two creatures and return the offspring, or None if incompatible."""
    if not can_breed(parent_a, parent_b):
        return None

    primary, secondary = get_breeding_result_type(
        parent_a.creature_type, parent_b.creature_type
    )

    # Determine offspring name
    name: str | None = None
    if secondary is not None:
        for creature_name, info in DUAL_TYPE_CREATURES.items():
            if info["primary"] == primary and info["secondary"] == secondary:
                name = creature_name
                break
    if name is None:
        name = random.choice([parent_a.name, parent_b.name])

    # Build move list from offspring types + normal
    type_keys = [primary]
    if secondary:
        type_keys.append(secondary)
    if "normal" not in type_keys:
        type_keys.append("normal")
    moves = get_moves_for_types(type_keys)

    # Determine ability
    ability: str | None = None
    if secondary is not None:
        for creature_name, info in DUAL_TYPE_CREATURES.items():
            if info["primary"] == primary and info["secondary"] == secondary:
                ability = info.get("ability")
                break
    if ability is None:
        parent_abilities = []
        for p in (parent_a, parent_b):
            ab = CREATURE_ABILITIES.get(p.name)
            if ab:
                parent_abilities.append(ab)
        if parent_abilities:
            ability = random.choice(parent_abilities)

    offspring = Creature(
        name=name,
        creature_type=primary,
        level=1,
        moves=moves,
        secondary_type=secondary,
        ability=ability,
    )
    return offspring


def get_breeding_preview(parent_a: Creature, parent_b: Creature) -> str:
    """Return a formatted string showing potential breeding result."""
    sorted_types = tuple(sorted([parent_a.creature_type, parent_b.creature_type]))
    possible = BREEDING_TABLE.get(sorted_types, [])
    types_str = " or ".join(possible) if possible else "unknown"
    return (
        f"🥚 Breeding Preview: {parent_a.name} ({parent_a.creature_type}) "
        f"+ {parent_b.name} ({parent_b.creature_type}) → {types_str} offspring"
    )
