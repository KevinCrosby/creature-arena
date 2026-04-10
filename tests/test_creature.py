"""Tests for the Creature and Move classes."""
from __future__ import annotations

import pytest
from creature import Creature, Move


class TestMove:
    def test_move_creation(self):
        m = Move("Ember", "fire", 6, "A small burst of flames")
        assert m.name == "Ember"
        assert m.move_type == "fire"
        assert m.power == 6
        assert m.description == "A small burst of flames"

    def test_move_default_description(self):
        m = Move("Tackle", "normal", 5)
        assert m.description == ""


class TestCreatureInit:
    def test_default_stats_level_1(self):
        c = Creature("Test", "fire")
        assert c.level == 1
        assert c.max_hp == 25  # 20 + 1*5
        assert c.hp == 25
        assert c.attack == 7   # 5 + 1*2
        assert c.defense == 4  # 3 + 1
        assert c.xp == 0
        assert c.xp_to_next == 10  # 1*10

    def test_stats_level_5(self):
        c = Creature("Test", "water", level=5)
        assert c.max_hp == 45  # 20 + 5*5
        assert c.attack == 15  # 5 + 5*2
        assert c.defense == 8  # 3 + 5

    def test_level_clamped_to_1(self):
        c = Creature("Test", "fire", level=0)
        assert c.level == 1

        c2 = Creature("Test", "fire", level=-5)
        assert c2.level == 1

    def test_hp_clamped_to_bounds(self):
        c = Creature("Test", "fire", hp=999)
        assert c.hp == c.max_hp

        c2 = Creature("Test", "fire", hp=-10)
        assert c2.hp == 0

    def test_xp_clamped_to_zero(self):
        c = Creature("Test", "fire", xp=-5)
        assert c.xp == 0

    def test_moves_stored(self):
        moves = [Move("Ember", "fire", 6)]
        c = Creature("Test", "fire", moves=moves)
        assert len(c.moves) == 1
        assert c.moves[0].name == "Ember"


class TestTakeDamage:
    def test_basic_damage(self):
        c = Creature("Test", "fire")  # defense = 4
        actual = c.take_damage(10)
        assert actual == 6  # 10 - 4
        assert c.hp == 25 - 6

    def test_minimum_damage_is_1(self):
        c = Creature("Test", "fire", level=10)  # defense = 13
        actual = c.take_damage(1)  # 1 - 13 would be negative
        assert actual == 1
        assert c.hp == c.max_hp - 1

    def test_hp_clamps_to_zero(self):
        c = Creature("Test", "fire")
        c.take_damage(999)
        assert c.hp == 0

    def test_hp_never_negative(self):
        c = Creature("Test", "fire")
        c.hp = 1
        c.take_damage(100)
        assert c.hp == 0


class TestFainted:
    def test_not_fainted_at_full_hp(self):
        c = Creature("Test", "fire")
        assert not c.is_fainted()

    def test_fainted_at_zero_hp(self):
        c = Creature("Test", "fire")
        c.hp = 0
        assert c.is_fainted()


class TestHeal:
    def test_heal_restores_max_hp(self):
        c = Creature("Test", "fire")
        c.take_damage(50)
        c.heal()
        assert c.hp == c.max_hp


class TestGainXP:
    def test_gain_xp_no_level_up(self):
        c = Creature("Test", "fire")  # xp_to_next = 10
        leveled = c.gain_xp(5)
        assert not leveled
        assert c.xp == 5

    def test_gain_xp_level_up(self):
        c = Creature("Test", "fire")  # xp_to_next = 10
        leveled = c.gain_xp(10)
        assert leveled
        assert c.level == 2

    def test_gain_xp_exactly_at_threshold(self):
        c = Creature("Test", "fire")
        leveled = c.gain_xp(10)  # exactly xp_to_next
        assert leveled
        assert c.level == 2
        assert c.xp == 0  # 10 - 10 = 0

    def test_gain_xp_overflow(self):
        c = Creature("Test", "fire")
        leveled = c.gain_xp(15)  # 5 over threshold
        assert leveled
        assert c.level == 2
        assert c.xp == 5  # 15 - 10 = 5

    def test_gain_zero_xp_returns_false(self):
        c = Creature("Test", "fire")
        assert not c.gain_xp(0)

    def test_gain_negative_xp_returns_false(self):
        c = Creature("Test", "fire")
        assert not c.gain_xp(-5)
        assert c.xp == 0

    def test_level_up_recalculates_stats(self):
        c = Creature("Test", "fire")
        old_max = c.max_hp
        c.gain_xp(10)
        assert c.max_hp == 30  # 20 + 2*5
        assert c.attack == 9  # 5 + 2*2
        assert c.defense == 5  # 3 + 2
        assert c.max_hp > old_max

    def test_level_up_increases_hp(self):
        c = Creature("Test", "fire")
        c.heal()  # full HP at level 1
        c.gain_xp(10)
        assert c.hp == c.max_hp  # Should be full after level up


class TestSerialization:
    def test_round_trip(self):
        moves = [Move("Ember", "fire", 6, "Flames")]
        c = Creature("Blazepup", "fire", level=3, moves=moves, xp=5)
        data = c.to_dict()
        c2 = Creature.from_dict(data)
        assert c2.name == "Blazepup"
        assert c2.creature_type == "fire"
        assert c2.level == 3
        assert c2.xp == 5
        assert c2.hp == c.hp
        assert len(c2.moves) == 1
        assert c2.moves[0].name == "Ember"

    def test_round_trip_preserves_damage(self):
        c = Creature("Test", "fire")
        c.take_damage(20)
        data = c.to_dict()
        c2 = Creature.from_dict(data)
        assert c2.hp == c.hp
        assert c2.hp < c2.max_hp

    def test_from_dict_missing_optional_fields(self):
        data = {"name": "Test", "creature_type": "fire"}
        c = Creature.from_dict(data)
        assert c.level == 1
        assert c.xp == 0
        assert c.moves == []

    def test_round_trip_unicode_name(self):
        c = Creature("⚡Sparky⚡", "electric")
        data = c.to_dict()
        c2 = Creature.from_dict(data)
        assert c2.name == "⚡Sparky⚡"

    def test_repr(self):
        c = Creature("Blazepup", "fire", level=3)
        r = repr(c)
        assert "Blazepup" in r
        assert "fire" in r
        assert "lv=3" in r
