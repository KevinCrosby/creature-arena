"""Turn-based battle engine with type advantages and critical hits."""
from __future__ import annotations

import random

from creature import Creature, Move
from data import TYPE_CHART, WEAKNESS_MULTIPLIER, RESISTANCE_MULTIPLIER

CRITICAL_HIT_CHANCE = 0.10
CRITICAL_HIT_MULTIPLIER = 1.5
BASE_XP_REWARD = 10


def get_type_multiplier(attack_type: str, defend_type: str) -> float:
    """Return the damage multiplier based on type matchup."""
    # Check if attacker has advantage
    if defend_type in TYPE_CHART.get(attack_type, set()):
        return WEAKNESS_MULTIPLIER
    # Check if defender resists (symmetric: if B beats A, A resists B)
    if attack_type in TYPE_CHART.get(defend_type, set()):
        return RESISTANCE_MULTIPLIER
    return 1.0


def calculate_damage(
    attacker: Creature, move: Move, defender: Creature, is_critical: bool = False
) -> tuple[int, float, bool]:
    """Calculate damage dealt. Returns (damage, multiplier, was_critical)."""
    base = attacker.attack + move.power
    type_mult = get_type_multiplier(move.move_type, defender.creature_type)
    crit_mult = CRITICAL_HIT_MULTIPLIER if is_critical else 1.0
    raw = int(base * type_mult * crit_mult)
    return raw, type_mult, is_critical


def roll_critical() -> bool:
    """Return True if this attack is a critical hit."""
    return random.random() < CRITICAL_HIT_CHANCE


def calculate_xp_reward(defeated: Creature) -> int:
    """XP gained from defeating a creature."""
    return max(1, BASE_XP_REWARD * defeated.level)


class BattleResult:
    """Outcome of a battle."""
    def __init__(self, winner: Creature, loser: Creature, xp_gained: int, turns: int):
        self.winner = winner
        self.loser = loser
        self.xp_gained = xp_gained
        self.turns = turns


class BattleEngine:
    """Manages a turn-based battle between two creatures."""

    def __init__(self, player_creature: Creature, opponent: Creature):
        self.player = player_creature
        self.opponent = opponent
        self.turn_count = 0
        self.log: list[str] = []

    def player_turn(self, move: Move) -> tuple[int, float, bool]:
        """Execute a player attack. Returns (damage, type_mult, was_crit)."""
        is_crit = roll_critical()
        raw_damage, type_mult, was_crit = calculate_damage(
            self.player, move, self.opponent, is_crit
        )
        actual = self.opponent.take_damage(raw_damage)
        self._log_attack(self.player, self.opponent, move, actual, type_mult, was_crit)
        return actual, type_mult, was_crit

    def opponent_turn(self) -> tuple[Move, int, float, bool]:
        """AI picks a move and attacks. Returns (move, damage, type_mult, was_crit)."""
        move = self._ai_pick_move()
        is_crit = roll_critical()
        raw_damage, type_mult, was_crit = calculate_damage(
            self.opponent, move, self.player, is_crit
        )
        actual = self.player.take_damage(raw_damage)
        self._log_attack(self.opponent, self.player, move, actual, type_mult, was_crit)
        return move, actual, type_mult, was_crit

    def _ai_pick_move(self) -> Move:
        """Simple AI: pick the move with the best type advantage, or random."""
        if not self.opponent.moves:
            return Move("Struggle", "normal", 4, "A desperate attack")
        best_move = self.opponent.moves[0]
        best_mult = 0.0
        for move in self.opponent.moves:
            mult = get_type_multiplier(move.move_type, self.player.creature_type)
            if mult > best_mult:
                best_mult = mult
                best_move = move
        return best_move

    def is_battle_over(self) -> bool:
        """Check if either creature has fainted."""
        return self.player.is_fainted() or self.opponent.is_fainted()

    def get_result(self) -> BattleResult | None:
        """Get the battle result. Attacker wins ties (simultaneous faint)."""
        if not self.is_battle_over():
            return None
        # Attacker (player) wins ties
        if self.opponent.is_fainted():
            xp = calculate_xp_reward(self.opponent)
            return BattleResult(self.player, self.opponent, xp, self.turn_count)
        else:
            return BattleResult(self.opponent, self.player, 0, self.turn_count)

    def _log_attack(
        self, attacker: Creature, defender: Creature,
        move: Move, damage: int, type_mult: float, was_crit: bool
    ) -> None:
        """Record a battle event."""
        msg = f"{attacker.name} used {move.name}! ({damage} damage)"
        if type_mult > 1.0:
            msg += " Super effective!"
        elif type_mult < 1.0:
            msg += " Not very effective..."
        if was_crit:
            msg += " Critical hit!"
        self.log.append(msg)
