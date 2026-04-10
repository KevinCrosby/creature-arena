"""Battle tournament / gauntlet mode."""
from __future__ import annotations

import random

from data import TOURNAMENT_TIERS, STARTER_CREATURES, get_moves_for_types
from creature import Creature


def get_available_tournaments(player_level: int) -> list[dict]:
    """Return tournament tiers where *player_level* falls within the level_range."""
    return [
        tier for tier in TOURNAMENT_TIERS
        if tier["level_range"][0] <= player_level <= tier["level_range"][1]
    ]


def generate_opponent(level: int) -> Creature:
    """Create a random opponent Creature at the given level."""
    template = random.choice(STARTER_CREATURES)
    if level <= 4:
        tier = 0
    elif level <= 8:
        tier = 1
    else:
        tier = 2
    moves = get_moves_for_types(template["moves"], tier=tier)
    return Creature(
        name=template["name"],
        creature_type=template["creature_type"],
        level=level,
        moves=moves,
    )


class TournamentRunner:
    """Manages a multi-round tournament gauntlet."""

    def __init__(self, tier: dict) -> None:
        self.tier = tier
        self.current_round: int = 0
        self.opponents: list[Creature] = []
        self.wins: int = 0
        self.losses: int = 0
        self.completed: bool = False
        self._generate_opponents()

    def _generate_opponents(self) -> None:
        """Pre-generate opponents at escalating levels within the tier's level_range."""
        lo, hi = self.tier["level_range"]
        rounds = self.tier["rounds"]
        for i in range(rounds):
            if rounds == 1:
                level = lo
            else:
                level = lo + round((hi - lo) * i / (rounds - 1))
            self.opponents.append(generate_opponent(level))

    def get_current_opponent(self) -> Creature | None:
        """Return the current round's opponent, or None if the tournament is done."""
        if self.current_round >= len(self.opponents):
            return None
        return self.opponents[self.current_round]

    def advance(self) -> bool:
        """Move to the next round. Return True if more rounds remain."""
        self.current_round += 1
        if self.current_round >= len(self.opponents):
            self.completed = True
            return False
        return True

    def record_win(self) -> None:
        self.wins += 1

    def record_loss(self) -> None:
        self.losses += 1

    def is_victory(self) -> bool:
        """True if all rounds completed with zero losses."""
        return self.completed and self.losses == 0

    def get_reward_gold(self) -> int:
        """Full reward on perfect victory, otherwise half per win."""
        if self.is_victory():
            return self.tier["reward_gold"]
        return (self.tier["reward_gold"] // 2) * self.wins // self.tier["rounds"]

    def get_status(self) -> str:
        """Formatted status string."""
        display_round = min(self.current_round + 1, self.tier["rounds"])
        return f"Round {display_round}/{self.tier['rounds']} — {self.tier['name']}"
