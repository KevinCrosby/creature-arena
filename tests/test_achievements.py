from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from achievements import AchievementTracker
from data import ACHIEVEMENT_DEFS


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------

def test_starts_with_all_achievements_locked():
    tracker = AchievementTracker()
    for ach in ACHIEVEMENT_DEFS:
        assert tracker.is_unlocked(ach["id"]) is False


# ---------------------------------------------------------------------------
# increment_stat / get_stat
# ---------------------------------------------------------------------------

def test_increment_stat_and_get_stat():
    tracker = AchievementTracker()
    tracker.increment_stat("creatures_caught", 5)
    assert tracker.get_stat("creatures_caught") == 5
    tracker.increment_stat("creatures_caught", 3)
    assert tracker.get_stat("creatures_caught") == 8


def test_get_stat_returns_zero_for_unknown():
    tracker = AchievementTracker()
    assert tracker.get_stat("totally_made_up") == 0


# ---------------------------------------------------------------------------
# Achievement unlocking via check_achievements
# ---------------------------------------------------------------------------

def test_first_catch_unlocks_at_1():
    tracker = AchievementTracker()
    tracker.increment_stat("creatures_caught", 1)
    newly = tracker.check_achievements()
    ids = [a["id"] for a in newly]
    assert "first_catch" in ids
    assert tracker.is_unlocked("first_catch")


def test_catch_10_unlocks_at_10():
    tracker = AchievementTracker()
    tracker.increment_stat("creatures_caught", 10)
    newly = tracker.check_achievements()
    ids = [a["id"] for a in newly]
    assert "catch_10" in ids


def test_win_first_battle_unlocks_at_1():
    tracker = AchievementTracker()
    tracker.increment_stat("battles_won", 1)
    newly = tracker.check_achievements()
    ids = [a["id"] for a in newly]
    assert "win_first_battle" in ids


def test_first_evolution_unlocks_at_1():
    tracker = AchievementTracker()
    tracker.increment_stat("evolutions", 1)
    newly = tracker.check_achievements()
    ids = [a["id"] for a in newly]
    assert "first_evolution" in ids


def test_check_achievements_returns_newly_unlocked_only():
    tracker = AchievementTracker()
    tracker.increment_stat("creatures_caught", 1)
    first_call = tracker.check_achievements()
    assert len(first_call) > 0
    # Second call with same stats should return nothing new
    second_call = tracker.check_achievements()
    assert len(second_call) == 0


# ---------------------------------------------------------------------------
# is_unlocked / get_unlocked
# ---------------------------------------------------------------------------

def test_is_unlocked_after_manual_unlock():
    tracker = AchievementTracker()
    tracker.unlock("first_catch")
    assert tracker.is_unlocked("first_catch") is True


def test_get_unlocked_returns_list_of_dicts():
    tracker = AchievementTracker()
    tracker.unlock("first_catch")
    tracker.unlock("win_first_battle")
    unlocked = tracker.get_unlocked()
    assert isinstance(unlocked, list)
    assert len(unlocked) == 2
    ids = [a["id"] for a in unlocked]
    assert "first_catch" in ids
    assert "win_first_battle" in ids


# ---------------------------------------------------------------------------
# get_progress_summary
# ---------------------------------------------------------------------------

def test_get_progress_summary():
    tracker = AchievementTracker()
    summary = tracker.get_progress_summary()
    assert isinstance(summary, str)
    assert "Achievements" in summary
    assert f"0/{len(ACHIEVEMENT_DEFS)}" in summary


# ---------------------------------------------------------------------------
# Serialization round-trip
# ---------------------------------------------------------------------------

def test_to_dict_from_dict_round_trip():
    tracker = AchievementTracker()
    tracker.increment_stat("creatures_caught", 5)
    tracker.increment_stat("battles_won", 2)
    tracker.unlock("first_catch")

    data = tracker.to_dict()
    tracker2 = AchievementTracker.from_dict(data)
    assert tracker2.is_unlocked("first_catch") is True
    assert tracker2.get_stat("creatures_caught") == 5
    assert tracker2.get_stat("battles_won") == 2


# ---------------------------------------------------------------------------
# Multiple achievements can unlock at once
# ---------------------------------------------------------------------------

def test_multiple_achievements_unlock_at_once():
    tracker = AchievementTracker()
    tracker.increment_stat("creatures_caught", 10)  # triggers first_catch AND catch_10
    tracker.increment_stat("battles_won", 1)         # triggers win_first_battle
    newly = tracker.check_achievements()
    ids = [a["id"] for a in newly]
    assert "first_catch" in ids
    assert "catch_10" in ids
    assert "win_first_battle" in ids
    assert len(ids) >= 3
