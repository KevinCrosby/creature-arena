"""Tests for the battle engine."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from creature import Creature, Move
from battle import (
    get_type_multiplier, calculate_damage, calculate_xp_reward,
    roll_critical, BattleEngine, CRITICAL_HIT_MULTIPLIER,
)
from data import WEAKNESS_MULTIPLIER, RESISTANCE_MULTIPLIER


class TestTypeMultiplier:
    def test_fire_beats_nature(self):
        assert get_type_multiplier("fire", "nature") == WEAKNESS_MULTIPLIER

    def test_water_beats_fire(self):
        assert get_type_multiplier("water", "fire") == WEAKNESS_MULTIPLIER

    def test_nature_beats_water(self):
        assert get_type_multiplier("nature", "water") == WEAKNESS_MULTIPLIER

    def test_electric_beats_water(self):
        assert get_type_multiplier("electric", "water") == WEAKNESS_MULTIPLIER

    def test_shadow_beats_electric(self):
        assert get_type_multiplier("shadow", "electric") == WEAKNESS_MULTIPLIER

    def test_nature_resists_fire(self):
        # Symmetric: fire beats nature, so nature resists fire... wait.
        # Actually: if fire is strong vs nature, then when nature attacks fire,
        # fire is in TYPE_CHART["nature"]'s strong set (water), not fire.
        # Let's check: nature → strong vs water. So fire attacking nature = 1.5x.
        # nature attacking fire: fire in TYPE_CHART["nature"]? nature beats water, not fire.
        # So check resistance: attack_type=nature, defend_type=fire.
        # TYPE_CHART.get("fire") = {"nature"}, and "nature" is in that set? 
        # attack_type="nature", so we check if "nature" in TYPE_CHART.get("fire") = {"nature"} → yes → RESISTANCE
        assert get_type_multiplier("nature", "fire") == RESISTANCE_MULTIPLIER

    def test_fire_resists_water(self):
        # water beats fire, so fire resists water attacks
        # attack_type="fire", defend_type="water" → check TYPE_CHART["fire"]={"nature"}, "water" not in it
        # Then check TYPE_CHART["water"]={"fire"}, "fire" in it → RESISTANCE
        assert get_type_multiplier("fire", "water") == RESISTANCE_MULTIPLIER

    def test_neutral_matchup(self):
        assert get_type_multiplier("fire", "electric") == 1.0

    def test_normal_is_neutral(self):
        assert get_type_multiplier("normal", "fire") == 1.0
        assert get_type_multiplier("normal", "water") == 1.0

    def test_same_type_neutral(self):
        # fire vs fire: TYPE_CHART["fire"]={"nature"}, "fire" not in it
        # then TYPE_CHART["fire"]={"nature"}, "fire" not in it → 1.0
        assert get_type_multiplier("fire", "fire") == 1.0


class TestCalculateDamage:
    def test_basic_damage(self):
        attacker = Creature("A", "fire", level=1)  # attack=7
        move = Move("Ember", "fire", 6)
        defender = Creature("D", "nature", level=1)
        damage, mult, crit = calculate_damage(attacker, move, defender, is_critical=False)
        assert mult == WEAKNESS_MULTIPLIER
        assert damage == int((7 + 6) * WEAKNESS_MULTIPLIER)
        assert not crit

    def test_critical_hit_damage(self):
        attacker = Creature("A", "fire", level=1)
        move = Move("Ember", "fire", 6)
        defender = Creature("D", "fire", level=1)  # neutral
        damage, mult, crit = calculate_damage(attacker, move, defender, is_critical=True)
        assert crit
        assert damage == int((7 + 6) * 1.0 * CRITICAL_HIT_MULTIPLIER)

    def test_super_effective_critical(self):
        attacker = Creature("A", "fire", level=1)
        move = Move("Ember", "fire", 6)
        defender = Creature("D", "nature", level=1)
        damage, mult, crit = calculate_damage(attacker, move, defender, is_critical=True)
        expected = int((7 + 6) * WEAKNESS_MULTIPLIER * CRITICAL_HIT_MULTIPLIER)
        assert damage == expected


class TestXPReward:
    def test_level_1_reward(self):
        c = Creature("Test", "fire", level=1)
        assert calculate_xp_reward(c) == 10

    def test_level_5_reward(self):
        c = Creature("Test", "fire", level=5)
        assert calculate_xp_reward(c) == 50

    def test_minimum_reward_is_1(self):
        c = Creature("Test", "fire", level=0)  # clamped to 1
        assert calculate_xp_reward(c) >= 1


class TestBattleEngine:
    def _make_creature(self, name: str, ctype: str, level: int = 1) -> Creature:
        return Creature(name, ctype, level=level, moves=[
            Move("Attack", ctype, 6),
            Move("Tackle", "normal", 5),
        ])

    def test_player_turn_deals_damage(self):
        player = self._make_creature("Player", "fire")
        opponent = self._make_creature("Opp", "nature")
        engine = BattleEngine(player, opponent)
        with patch("battle.roll_critical", return_value=False):
            damage, mult, crit = engine.player_turn(player.moves[0])
        assert damage > 0
        assert opponent.hp < opponent.max_hp

    def test_opponent_turn_deals_damage(self):
        player = self._make_creature("Player", "fire")
        opponent = self._make_creature("Opp", "water")
        engine = BattleEngine(player, opponent)
        with patch("battle.roll_critical", return_value=False):
            move, damage, mult, crit = engine.opponent_turn()
        assert damage > 0
        assert player.hp < player.max_hp

    def test_ai_picks_best_type_move(self):
        player = self._make_creature("Player", "nature")
        opponent = Creature("Opp", "fire", moves=[
            Move("Tackle", "normal", 5),
            Move("Ember", "fire", 6),  # Super effective vs nature
        ])
        engine = BattleEngine(player, opponent)
        with patch("battle.roll_critical", return_value=False):
            move, _, _, _ = engine.opponent_turn()
        assert move.move_type == "fire"

    def test_battle_over_when_fainted(self):
        player = self._make_creature("Player", "fire")
        opponent = self._make_creature("Opp", "nature")
        opponent.hp = 0
        engine = BattleEngine(player, opponent)
        assert engine.is_battle_over()

    def test_player_wins_on_opponent_faint(self):
        player = self._make_creature("Player", "fire")
        opponent = self._make_creature("Opp", "nature")
        opponent.hp = 0
        engine = BattleEngine(player, opponent)
        result = engine.get_result()
        assert result is not None
        assert result.winner is player

    def test_attacker_wins_simultaneous_faint(self):
        player = self._make_creature("Player", "fire")
        opponent = self._make_creature("Opp", "nature")
        player.hp = 0
        opponent.hp = 0
        engine = BattleEngine(player, opponent)
        result = engine.get_result()
        assert result is not None
        # Opponent fainted, so player wins (attacker wins ties)
        assert result.winner is player

    def test_no_result_when_both_alive(self):
        player = self._make_creature("Player", "fire")
        opponent = self._make_creature("Opp", "nature")
        engine = BattleEngine(player, opponent)
        assert engine.get_result() is None

    def test_ai_uses_struggle_with_no_moves(self):
        player = self._make_creature("Player", "fire")
        opponent = Creature("Opp", "water", moves=[])
        engine = BattleEngine(player, opponent)
        with patch("battle.roll_critical", return_value=False):
            move, damage, _, _ = engine.opponent_turn()
        assert move.name == "Struggle"
        assert damage > 0

    def test_battle_log_records_attacks(self):
        player = self._make_creature("Player", "fire")
        opponent = self._make_creature("Opp", "nature")
        engine = BattleEngine(player, opponent)
        with patch("battle.roll_critical", return_value=False):
            engine.player_turn(player.moves[0])
        assert len(engine.log) == 1
        assert "Player" in engine.log[0]
