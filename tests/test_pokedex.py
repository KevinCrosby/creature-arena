from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pokedex import Pokedex


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------

def test_starts_empty():
    dex = Pokedex()
    assert dex.get_seen_count() == 0
    assert dex.get_caught_count() == 0
    assert len(dex.areas_visited) == 0


# ---------------------------------------------------------------------------
# mark_seen / mark_caught / mark_area
# ---------------------------------------------------------------------------

def test_mark_seen_adds_to_seen():
    dex = Pokedex()
    dex.mark_seen("Blazepup")
    assert dex.is_seen("Blazepup") is True
    assert dex.is_caught("Blazepup") is False


def test_mark_caught_adds_to_both_seen_and_caught():
    dex = Pokedex()
    dex.mark_caught("Aquafin")
    assert dex.is_seen("Aquafin") is True
    assert dex.is_caught("Aquafin") is True


def test_mark_area_adds_to_areas_visited():
    dex = Pokedex()
    dex.mark_area("Scorched Plains")
    assert "Scorched Plains" in dex.areas_visited


# ---------------------------------------------------------------------------
# is_seen / is_caught
# ---------------------------------------------------------------------------

def test_is_seen_false_for_unknown():
    dex = Pokedex()
    assert dex.is_seen("Unknown") is False


def test_is_caught_false_for_unseen():
    dex = Pokedex()
    assert dex.is_caught("Unknown") is False


# ---------------------------------------------------------------------------
# get_completion_rate
# ---------------------------------------------------------------------------

def test_get_completion_rate():
    dex = Pokedex()
    assert dex.get_completion_rate() == 0.0
    dex.mark_caught("Blazepup")
    rate = dex.get_completion_rate()
    assert 0.0 < rate <= 1.0


# ---------------------------------------------------------------------------
# get_seen_count / get_caught_count
# ---------------------------------------------------------------------------

def test_get_seen_count():
    dex = Pokedex()
    dex.mark_seen("Blazepup")
    dex.mark_seen("Aquafin")
    assert dex.get_seen_count() == 2


def test_get_caught_count():
    dex = Pokedex()
    dex.mark_caught("Blazepup")
    dex.mark_caught("Aquafin")
    assert dex.get_caught_count() == 2


# ---------------------------------------------------------------------------
# get_summary
# ---------------------------------------------------------------------------

def test_get_summary_returns_formatted_string():
    dex = Pokedex()
    dex.mark_caught("Blazepup")
    summary = dex.get_summary()
    assert isinstance(summary, str)
    assert "seen" in summary.lower() or "Pokédex" in summary
    assert "caught" in summary.lower()


# ---------------------------------------------------------------------------
# Serialization round-trip
# ---------------------------------------------------------------------------

def test_to_dict_from_dict_round_trip():
    dex = Pokedex()
    dex.mark_seen("Blazepup")
    dex.mark_caught("Aquafin")
    dex.mark_area("Crystal Lake")

    data = dex.to_dict()
    dex2 = Pokedex.from_dict(data)
    assert dex2.is_seen("Blazepup")
    assert dex2.is_caught("Aquafin")
    assert dex2.is_seen("Aquafin")
    assert "Crystal Lake" in dex2.areas_visited
