"""Tests for complex battle interactions: moves, speed, defend, status, and type matchups."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from creature import Creature, Move
from battle import (
    apply_move_effect, calculate_damage, get_type_multiplier,
    BattleEngine,
)
from data import WEAKNESS_MULTIPLIER, RESISTANCE_MULTIPLIER


# -- Helpers --

def make_creature(name: str = "TestMon", creature_type: str = "fire",
                  level: int = 5, **kwargs) -> Creature:
    return Creature(name=name, creature_type=creature_type, level=level, **kwargs)


def poison_move() -> Move:
    return Move("Toxic Spit", "nature", 4, "Poison attack",
                effect="poison", effect_chance=0.4, effect_duration=3)


def no_effect_move() -> Move:
    return Move("Tackle", "normal", 5, "Basic attack")


# ---------------------------------------------------------------------------
# TestMoveEffects
# ---------------------------------------------------------------------------

class TestMoveEffects:
    def test_apply_move_effect_poison(self):
        target = make_creature()
        move = poison_move()
        with patch("battle.random.random", return_value=0.1):
            effect = apply_move_effect(move, target)
        assert effect == "poison"
        assert "poison" in target.status_effects

    def test_apply_move_effect_chance(self):
        target = make_creature()
        move = poison_move()  # effect_chance = 0.4
        # Roll above threshold → no effect
        with patch("battle.random.random", return_value=0.5):
            effect = apply_move_effect(move, target)
        assert effect is None
        assert "poison" not in target.status_effects

    def test_move_without_effect(self):
        target = make_creature()
        move = no_effect_move()
        result = apply_move_effect(move, target)
        assert result is None

    def test_effect_not_applied_when_already_active(self):
        target = make_creature()
        target.apply_status("poison", 3)
        move = poison_move()
        with patch("battle.random.random", return_value=0.1):
            effect = apply_move_effect(move, target)
        assert effect is None  # Already poisoned


# ---------------------------------------------------------------------------
# TestSpeedTurnOrder
# ---------------------------------------------------------------------------

class TestSpeedTurnOrder:
    def test_faster_creature_goes_first(self):
        fast = make_creature(name="Fast", level=10)  # speed = 14
        slow = make_creature(name="Slow", level=1)   # speed = 5
        engine = BattleEngine(slow, fast)
        order = engine.get_turn_order()
        assert order == ["opponent", "player"]

    def test_equal_speed_player_first(self):
        p = make_creature(name="Player", level=5)
        o = make_creature(name="Opponent", level=5)
        engine = BattleEngine(p, o)
        order = engine.get_turn_order()
        assert order == ["player", "opponent"]

    def test_speed_varies_by_level(self):
        low = make_creature(level=1)
        high = make_creature(level=5)
        assert high.speed > low.speed


# ---------------------------------------------------------------------------
# TestDefendAction
# ---------------------------------------------------------------------------

class TestDefendAction:
    def test_player_defend_sets_flag(self):
        p = make_creature(name="Player")
        o = make_creature(name="Opponent")
        engine = BattleEngine(p, o)
        engine.player_defend()
        assert p.is_defending is True

    def test_defend_reduces_damage(self):
        p = make_creature(name="Player", level=5)
        o = make_creature(name="Opponent", level=5)
        move = no_effect_move()

        # Damage without defend
        p1 = make_creature(name="P1", level=5)
        raw, _, _ = calculate_damage(o, move, p1)
        dmg_no_defend = p1.take_damage(raw)

        # Damage with defend
        p2 = make_creature(name="P2", level=5)
        p2.is_defending = True
        raw2, _, _ = calculate_damage(o, move, p2)
        dmg_with_defend = p2.take_damage(raw2)

        assert dmg_with_defend < dmg_no_defend

    def test_defend_resets_after_hit(self):
        c = make_creature()
        c.is_defending = True
        c.take_damage(10)
        assert c.is_defending is False


# ---------------------------------------------------------------------------
# TestStatusInBattle
# ---------------------------------------------------------------------------

class TestStatusInBattle:
    def test_process_turn_start_poison_damage(self):
        p = make_creature(name="Player")
        o = make_creature(name="Opponent")
        engine = BattleEngine(p, o)
        p.apply_status("poison", 3)
        hp_before = p.hp
        results = engine.process_turn_start(p)
        assert any(eff == "poison" and dmg > 0 for eff, dmg in results)
        assert p.hp < hp_before

    def test_stunned_creature_skips(self):
        c = make_creature()
        c.apply_status("stun", 1)
        assert c.is_stunned() is True

    def test_shield_reduces_battle_damage(self):
        unshielded = make_creature(name="Unshielded", level=5)
        shielded = make_creature(name="Shielded", level=5)
        shielded.apply_status("shield", 2)

        attacker = make_creature(name="Attacker", level=5)
        move = Move("Strike", "fire", 10, "Big hit")

        raw, _, _ = calculate_damage(attacker, move, unshielded)
        dmg_no_shield = unshielded.take_damage(raw)

        raw2, _, _ = calculate_damage(attacker, move, shielded)
        dmg_with_shield = shielded.take_damage(raw2)

        assert dmg_with_shield < dmg_no_shield


# ---------------------------------------------------------------------------
# TestNewTypeMatchups
# ---------------------------------------------------------------------------

class TestNewTypeMatchups:
    def test_ice_beats_nature(self):
        assert get_type_multiplier("ice", "nature") == WEAKNESS_MULTIPLIER

    def test_ice_beats_shadow(self):
        assert get_type_multiplier("ice", "shadow") == WEAKNESS_MULTIPLIER

    def test_psychic_beats_shadow(self):
        assert get_type_multiplier("psychic", "shadow") == WEAKNESS_MULTIPLIER

    def test_fire_beats_ice(self):
        assert get_type_multiplier("fire", "ice") == WEAKNESS_MULTIPLIER

    def test_nature_beats_electric(self):
        assert get_type_multiplier("nature", "electric") == WEAKNESS_MULTIPLIER
