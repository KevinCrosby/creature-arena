from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from creature import Creature, Move
from breeding import can_breed, breed_creatures, get_breeding_preview
from trading import export_creature, import_creature, validate_trade_code, get_trade_summary
from tournament import get_available_tournaments, generate_opponent, TournamentRunner
from story import StoryProgress
from replay import BattleReplay, ReplayManager
from data import TOURNAMENT_TIERS


# ===========================================================================
# Helpers
# ===========================================================================

def _make_creature(name="TestMon", ctype="fire", level=5, hp=None):
    c = Creature(
        name=name,
        creature_type=ctype,
        level=level,
        moves=[Move("Tackle", "normal", 5)],
    )
    if hp is not None:
        c.hp = hp
    return c


# ===========================================================================
# Breeding tests
# ===========================================================================

def test_can_breed_requires_level_5_plus():
    a = _make_creature(level=5, ctype="fire")
    b = _make_creature(name="B", level=4, ctype="water")
    assert can_breed(a, b) is False

    b2 = _make_creature(name="B2", level=5, ctype="water")
    assert can_breed(a, b2) is True


def test_can_breed_rejects_fainted():
    a = _make_creature(level=5, ctype="fire")
    b = _make_creature(name="B", level=5, ctype="water")
    b.hp = 0
    assert can_breed(a, b) is False


def test_can_breed_rejects_same_instance():
    a = _make_creature(level=5, ctype="fire")
    assert can_breed(a, a) is False


def test_can_breed_rejects_incompatible_types():
    a = _make_creature(level=5, ctype="fire")
    b = _make_creature(name="B", level=5, ctype="fire")
    # (fire, fire) is not in BREEDING_TABLE
    assert can_breed(a, b) is False


def test_breed_creatures_returns_creature_with_correct_type():
    a = _make_creature(level=5, ctype="fire")
    b = _make_creature(name="B", level=5, ctype="water")
    offspring = breed_creatures(a, b)
    assert offspring is not None
    assert isinstance(offspring, Creature)
    assert offspring.creature_type in ("fire", "water")


def test_breed_creatures_returns_none_if_cant_breed():
    a = _make_creature(level=2, ctype="fire")
    b = _make_creature(name="B", level=2, ctype="water")
    assert breed_creatures(a, b) is None


def test_get_breeding_preview_returns_string():
    a = _make_creature(level=5, ctype="fire")
    b = _make_creature(name="B", level=5, ctype="water")
    preview = get_breeding_preview(a, b)
    assert isinstance(preview, str)
    assert "Breeding Preview" in preview


# ===========================================================================
# Trading tests
# ===========================================================================

def test_export_creature_starts_with_prefix():
    c = _make_creature()
    code = export_creature(c)
    assert code.startswith("CA1-")


def test_import_creature_round_trips():
    c = _make_creature(name="Blazepup", ctype="fire", level=7)
    code = export_creature(c)
    imported = import_creature(code)
    assert imported is not None
    assert imported.name == "Blazepup"
    assert imported.creature_type == "fire"
    assert imported.level == 7


def test_import_creature_returns_none_for_invalid():
    assert import_creature("INVALID_CODE") is None
    assert import_creature("") is None
    assert import_creature("CA1-!!!notbase64") is None


def test_validate_trade_code():
    c = _make_creature()
    code = export_creature(c)
    assert validate_trade_code(code) is True
    assert validate_trade_code("garbage") is False


def test_get_trade_summary_returns_string():
    c = _make_creature(name="Blazepup", level=3)
    code = export_creature(c)
    summary = get_trade_summary(code)
    assert summary is not None
    assert "Blazepup" in summary
    assert "Lv.3" in summary


# ===========================================================================
# Tournament tests
# ===========================================================================

def test_get_available_tournaments_filters_by_level():
    # Level 1 should only match Bronze Cup (1-4)
    available = get_available_tournaments(1)
    names = [t["name"] for t in available]
    assert "Bronze Cup" in names
    assert "Champion Cup" not in names


def test_get_available_tournaments_mid_level():
    # Level 7 should match Silver (3-7) and Gold (6-10)
    available = get_available_tournaments(7)
    names = [t["name"] for t in available]
    assert "Silver Cup" in names
    assert "Gold Cup" in names


def test_generate_opponent_creates_creature_at_correct_level():
    opp = generate_opponent(5)
    assert isinstance(opp, Creature)
    assert opp.level == 5
    assert len(opp.moves) > 0


def test_tournament_runner_tracks_rounds():
    tier = TOURNAMENT_TIERS[0]  # Bronze Cup, 3 rounds
    runner = TournamentRunner(tier)
    assert runner.current_round == 0
    assert runner.wins == 0
    assert runner.losses == 0
    assert runner.completed is False
    opp = runner.get_current_opponent()
    assert opp is not None


def test_tournament_runner_is_victory_after_all_wins():
    tier = TOURNAMENT_TIERS[0]  # Bronze Cup, 3 rounds
    runner = TournamentRunner(tier)
    for _ in range(tier["rounds"]):
        runner.record_win()
        runner.advance()
    assert runner.completed is True
    assert runner.is_victory() is True


def test_tournament_runner_not_victory_with_loss():
    tier = TOURNAMENT_TIERS[0]
    runner = TournamentRunner(tier)
    runner.record_win()
    runner.advance()
    runner.record_loss()
    runner.advance()
    runner.record_win()
    runner.advance()
    assert runner.completed is True
    assert runner.is_victory() is False


# ===========================================================================
# Story tests
# ===========================================================================

def test_story_starts_at_chapter_1():
    sp = StoryProgress()
    assert sp.current_chapter == 1
    assert sp.story_complete is False


def test_create_boss_returns_creature_with_bonus_hp():
    sp = StoryProgress()
    boss = sp.create_boss()
    assert isinstance(boss, Creature)
    base_max_hp = 20 + (boss.level * 5)
    bonus = base_max_hp // 2
    expected_max_hp = base_max_hp + bonus
    assert boss.max_hp == expected_max_hp
    assert boss.hp == boss.max_hp


def test_complete_chapter_advances():
    sp = StoryProgress()
    assert sp.current_chapter == 1
    ch = sp.complete_chapter()
    assert ch["id"] == 1
    assert sp.current_chapter == 2


def test_story_complete_after_all_5_chapters():
    sp = StoryProgress()
    for _ in range(5):
        sp.complete_chapter()
    assert sp.story_complete is True


# ===========================================================================
# Replay tests
# ===========================================================================

def test_battle_replay_records_events():
    replay = BattleReplay("Player", "Wild Blazepup")
    replay.record_attack("Player", "Tackle", 10, False, 1.0, None)
    replay.record_defend("Wild Blazepup")
    replay.record_status("Wild Blazepup", "poison", 3)
    assert len(replay.events) == 3
    assert replay.events[0]["type"] == "attack"
    assert replay.events[1]["type"] == "defend"
    assert replay.events[2]["type"] == "status_effect"


def test_battle_replay_get_summary():
    replay = BattleReplay("Player", "Wild Blazepup")
    replay.record_attack("Player", "Tackle", 10, False, 1.0, None)
    replay.set_result("Player")
    summary = replay.get_summary()
    assert isinstance(summary, str)
    assert "Player" in summary
    assert "Wild Blazepup" in summary
    assert "Win" in summary


def test_battle_replay_to_dict_from_dict():
    replay = BattleReplay("Player", "Opponent")
    replay.record_attack("Player", "Ember", 15, True, 1.5, "burn")
    replay.set_result("Player")

    data = replay.to_dict()
    replay2 = BattleReplay.from_dict(data)
    assert replay2.player_name == "Player"
    assert replay2.opponent_name == "Opponent"
    assert replay2.result == "win"
    assert len(replay2.events) == 1
