"""Tests for save/load functionality."""
from __future__ import annotations

import json
import os
import tempfile

import pytest
from creature import Creature, Move
from collection import Collection
from save_manager import save_game, load_game, validate_creature, SCHEMA_VERSION


@pytest.fixture
def tmp_save_path(tmp_path):
    """Provide a temporary save file path."""
    return str(tmp_path / "test_save.json")


@pytest.fixture
def sample_collection():
    """Create a small test collection."""
    c1 = Creature("Blazepup", "fire", level=3, moves=[
        Move("Ember", "fire", 6, "Flames"),
    ], xp=5)
    c2 = Creature("Aquafin", "water", level=2, moves=[
        Move("Splash", "water", 6, "Water jet"),
    ])
    return Collection(creatures=[c1, c2], active_index=1)


class TestSaveLoad:
    def test_round_trip(self, tmp_save_path, sample_collection):
        assert save_game(sample_collection, tmp_save_path)
        loaded = load_game(tmp_save_path)
        assert loaded is not None
        assert len(loaded.creatures) == 2
        assert loaded.creatures[0].name == "Blazepup"
        assert loaded.creatures[0].level == 3
        assert loaded.creatures[0].xp == 5
        assert loaded.creatures[1].name == "Aquafin"
        assert loaded.active_index == 1

    def test_preserves_damage(self, tmp_save_path):
        c = Creature("Test", "fire")
        c.take_damage(50)
        col = Collection(creatures=[c])
        save_game(col, tmp_save_path)
        loaded = load_game(tmp_save_path)
        assert loaded is not None
        assert loaded.creatures[0].hp == c.hp
        assert loaded.creatures[0].hp < loaded.creatures[0].max_hp

    def test_schema_version_present(self, tmp_save_path, sample_collection):
        save_game(sample_collection, tmp_save_path)
        with open(tmp_save_path) as f:
            data = json.load(f)
        assert "schema_version" in data
        assert data["schema_version"] == SCHEMA_VERSION

    def test_load_nonexistent_returns_none(self, tmp_path):
        result = load_game(str(tmp_path / "nope.json"))
        assert result is None

    def test_load_corrupted_json(self, tmp_save_path):
        with open(tmp_save_path, "w") as f:
            f.write("{corrupted json!!!}")
        result = load_game(tmp_save_path)
        assert result is None

    def test_load_missing_schema_version(self, tmp_save_path):
        data = {"collection": {"creatures": [], "active_index": 0}}
        with open(tmp_save_path, "w") as f:
            json.dump(data, f)
        result = load_game(tmp_save_path)
        assert result is None

    def test_load_future_schema_version(self, tmp_save_path):
        data = {
            "schema_version": 999,
            "collection": {"creatures": [], "active_index": 0},
        }
        with open(tmp_save_path, "w") as f:
            json.dump(data, f)
        result = load_game(tmp_save_path)
        assert result is None

    def test_load_missing_collection(self, tmp_save_path):
        data = {"schema_version": 1}
        with open(tmp_save_path, "w") as f:
            json.dump(data, f)
        result = load_game(tmp_save_path)
        assert result is None

    def test_unicode_creature_names(self, tmp_save_path):
        c = Creature("⚡Sparky⚡", "electric")
        col = Collection(creatures=[c])
        save_game(col, tmp_save_path)
        loaded = load_game(tmp_save_path)
        assert loaded is not None
        assert loaded.creatures[0].name == "⚡Sparky⚡"

    def test_emoji_in_move_description(self, tmp_save_path):
        c = Creature("Test", "fire", moves=[
            Move("🔥Blast", "fire", 8, "A 🔥 explosion!")
        ])
        col = Collection(creatures=[c])
        save_game(col, tmp_save_path)
        loaded = load_game(tmp_save_path)
        assert loaded is not None
        assert loaded.creatures[0].moves[0].description == "A 🔥 explosion!"

    def test_duplicate_creature_names(self, tmp_save_path):
        c1 = Creature("Blazepup", "fire")
        c2 = Creature("Blazepup", "fire", level=3)
        col = Collection(creatures=[c1, c2])
        save_game(col, tmp_save_path)
        loaded = load_game(tmp_save_path)
        assert loaded is not None
        assert len(loaded.creatures) == 2
        assert loaded.creatures[0].level == 1
        assert loaded.creatures[1].level == 3


class TestValidation:
    def test_valid_creature(self):
        c = Creature("Test", "fire", level=3)
        assert validate_creature(c)

    def test_invalid_level(self):
        c = Creature("Test", "fire")
        c.level = 0
        assert not validate_creature(c)

    def test_invalid_max_hp(self):
        c = Creature("Test", "fire")
        c.max_hp = 999
        assert not validate_creature(c)

    def test_hp_over_max(self):
        c = Creature("Test", "fire")
        c.hp = c.max_hp + 10
        assert not validate_creature(c)

    def test_negative_hp(self):
        c = Creature("Test", "fire")
        c.hp = -1
        assert not validate_creature(c)

    def test_invalid_type(self):
        c = Creature("Test", "dragon")
        assert not validate_creature(c)

    def test_load_with_invalid_creature_repairs(self, tmp_save_path):
        """Save valid data, corrupt it manually, load should repair."""
        c = Creature("Test", "fire", level=3)
        col = Collection(creatures=[c])
        save_game(col, tmp_save_path)
        # Corrupt the max_hp in the saved file
        with open(tmp_save_path) as f:
            data = json.load(f)
        data["collection"]["creatures"][0]["level"] = 3
        # Manually set wrong hp to trigger repair
        data["collection"]["creatures"][0]["hp"] = 999
        with open(tmp_save_path, "w") as f:
            json.dump(data, f)
        loaded = load_game(tmp_save_path)
        assert loaded is not None
        # HP should be clamped during Creature.__init__
        assert loaded.creatures[0].hp <= loaded.creatures[0].max_hp
