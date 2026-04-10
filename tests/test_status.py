"""Tests for the status effect system."""
from __future__ import annotations

import pytest
from creature import Creature, Move


# -- Helpers --

def make_creature(**kwargs) -> Creature:
    defaults = {"name": "TestMon", "creature_type": "fire", "level": 5}
    defaults.update(kwargs)
    return Creature(**defaults)


# ---------------------------------------------------------------------------
# TestApplyStatus
# ---------------------------------------------------------------------------

class TestApplyStatus:
    def test_apply_poison(self):
        c = make_creature()
        assert c.apply_status("poison", 3) is True
        assert "poison" in c.status_effects
        assert c.status_effects["poison"] == 3

    def test_apply_burn(self):
        c = make_creature()
        assert c.apply_status("burn", 3) is True
        assert "burn" in c.status_effects
        assert c.status_effects["burn"] == 3

    def test_apply_stun(self):
        c = make_creature()
        assert c.apply_status("stun", 1) is True
        assert "stun" in c.status_effects
        assert c.status_effects["stun"] == 1

    def test_apply_shield(self):
        c = make_creature()
        assert c.apply_status("shield", 2) is True
        assert "shield" in c.status_effects
        assert c.status_effects["shield"] == 2

    def test_apply_boost(self):
        c = make_creature()
        assert c.apply_status("boost", 3) is True
        assert "boost" in c.status_effects
        assert c.status_effects["boost"] == 3

    def test_no_stack(self):
        c = make_creature()
        assert c.apply_status("poison", 3) is True
        assert c.apply_status("poison", 5) is False
        # Duration should remain at original value
        assert c.status_effects["poison"] == 3

    def test_multiple_effects(self):
        c = make_creature()
        c.apply_status("poison", 3)
        c.apply_status("burn", 2)
        assert "poison" in c.status_effects
        assert "burn" in c.status_effects
        assert len(c.status_effects) == 2


# ---------------------------------------------------------------------------
# TestTickStatuses
# ---------------------------------------------------------------------------

class TestTickStatuses:
    def test_poison_damage(self):
        c = make_creature(level=5)  # max_hp = 45
        c.apply_status("poison", 3)
        hp_before = c.hp
        results = c.tick_statuses()
        expected_damage = max(1, c.max_hp // 8)  # 45 // 8 = 5
        assert any(eff == "poison" and dmg == expected_damage for eff, dmg in results)
        assert c.hp == hp_before - expected_damage

    def test_burn_damage(self):
        c = make_creature(level=5)  # max_hp = 45
        c.apply_status("burn", 3)
        hp_before = c.hp
        results = c.tick_statuses()
        expected_damage = max(1, c.max_hp // 6)  # 45 // 6 = 7
        assert any(eff == "burn" and dmg == expected_damage for eff, dmg in results)
        assert c.hp == hp_before - expected_damage

    def test_stun_detected(self):
        c = make_creature()
        c.apply_status("stun", 2)
        assert c.is_stunned() is True

    def test_effect_expires(self):
        c = make_creature()
        c.apply_status("shield", 1)
        assert "shield" in c.status_effects
        c.tick_statuses()
        assert "shield" not in c.status_effects

    def test_poison_3_turns(self):
        c = make_creature()
        c.apply_status("poison", 3)
        for _ in range(3):
            assert "poison" in c.status_effects
            c.tick_statuses()
        assert "poison" not in c.status_effects

    def test_hp_never_below_zero(self):
        c = make_creature(level=1)  # max_hp = 25
        c.hp = 1
        c.apply_status("poison", 3)
        c.tick_statuses()
        assert c.hp >= 0


# ---------------------------------------------------------------------------
# TestEffectiveStats
# ---------------------------------------------------------------------------

class TestEffectiveStats:
    def test_boost_increases_attack(self):
        c = make_creature(level=5)  # attack = 15
        base_atk = c.attack
        c.apply_status("boost", 3)
        assert c.get_effective_attack() == int(base_atk * 1.5)

    def test_shield_increases_defense(self):
        c = make_creature(level=5)  # defense = 8
        base_def = c.defense
        c.apply_status("shield", 2)
        assert c.get_effective_defense() == int(base_def * 1.5)

    def test_defend_doubles_defense(self):
        c = make_creature(level=5)
        base_def = c.defense
        c.is_defending = True
        assert c.get_effective_defense() == base_def * 2

    def test_shield_and_defend_stack(self):
        c = make_creature(level=5)
        base_def = c.defense
        c.apply_status("shield", 2)
        c.is_defending = True
        # Shield first (1.5x), then defend doubles
        expected = int(base_def * 1.5) * 2
        assert c.get_effective_defense() == expected

    def test_no_effects_normal_stats(self):
        c = make_creature(level=5)
        assert c.get_effective_attack() == c.attack
        assert c.get_effective_defense() == c.defense


# ---------------------------------------------------------------------------
# TestClearStatuses
# ---------------------------------------------------------------------------

class TestClearStatuses:
    def test_heal_clears_all(self):
        c = make_creature()
        c.apply_status("poison", 3)
        c.apply_status("burn", 2)
        c.is_defending = True
        c.hp = 1
        c.heal()
        assert c.hp == c.max_hp
        assert len(c.status_effects) == 0
        assert c.is_defending is False

    def test_clear_statuses_method(self):
        c = make_creature()
        c.apply_status("poison", 3)
        c.apply_status("shield", 2)
        c.is_defending = True
        c.clear_statuses()
        assert len(c.status_effects) == 0
        assert c.is_defending is False
