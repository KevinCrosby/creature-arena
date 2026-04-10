"""Autonomous creature evolution system."""
from __future__ import annotations

from creature import Creature
from data import EVOLUTION_CHAINS, get_moves_for_types


def check_evolution(creature: Creature) -> dict | None:
    """Check if a creature is ready to evolve. Returns evolution data or None."""
    chain = EVOLUTION_CHAINS.get(creature.name)
    if chain is None:
        return None
    if creature.level >= chain["level"]:
        return chain
    return None


def evolve_creature(creature: Creature) -> str | None:
    """Attempt to evolve a creature. Returns the new name if evolved, None otherwise.

    This is called automatically after each level-up. Evolution is autonomous —
    it happens without player input when the level threshold is reached.
    """
    chain = check_evolution(creature)
    if chain is None:
        return None

    old_name = creature.name
    new_name = chain["evolves_to"]
    stat_bonus = chain.get("stat_bonus", 5)

    # Get new moves based on the evolution's move type keys
    new_move_keys = chain.get("new_moves", [])
    # Use tier based on evolution stage to get progressively better moves
    tier = creature.evolution_stage + 1
    new_moves = get_moves_for_types(new_move_keys, tier=tier)

    # Filter out moves the creature already knows (by name)
    existing_move_names = {m.name for m in creature.moves}
    unique_new_moves = [m for m in new_moves if m.name not in existing_move_names]

    creature.evolve(new_name, new_moves=unique_new_moves, stat_bonus=stat_bonus)
    return new_name
