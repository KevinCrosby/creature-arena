from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from weather import WeatherSystem
from data import WEATHER_CONDITIONS, WEATHER_BOOST, WEATHER_WEAKEN


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------

def test_starts_with_clear_weather():
    ws = WeatherSystem()
    assert ws.current == "Clear"
    assert ws.turns_remaining == 0


# ---------------------------------------------------------------------------
# roll_weather
# ---------------------------------------------------------------------------

def test_roll_weather_returns_valid_weather():
    ws = WeatherSystem()
    result = ws.roll_weather()
    assert result in WEATHER_CONDITIONS
    assert ws.turns_remaining >= 3


# ---------------------------------------------------------------------------
# get_description
# ---------------------------------------------------------------------------

def test_get_description_returns_nonempty_string():
    ws = WeatherSystem()
    desc = ws.get_description()
    assert isinstance(desc, str)
    assert len(desc) > 0


# ---------------------------------------------------------------------------
# get_damage_modifier
# ---------------------------------------------------------------------------

def test_damage_modifier_boosted_type():
    ws = WeatherSystem()
    ws.current = "Sunny"
    assert ws.get_damage_modifier("fire") == WEATHER_BOOST


def test_damage_modifier_weakened_type():
    ws = WeatherSystem()
    ws.current = "Sunny"
    assert ws.get_damage_modifier("water") == WEATHER_WEAKEN
    assert ws.get_damage_modifier("ice") == WEATHER_WEAKEN


def test_damage_modifier_unaffected_type():
    ws = WeatherSystem()
    ws.current = "Sunny"
    assert ws.get_damage_modifier("electric") == 1.0
    assert ws.get_damage_modifier("shadow") == 1.0


def test_clear_weather_returns_1_for_all_types():
    ws = WeatherSystem()
    ws.current = "Clear"
    for move_type in ("fire", "water", "nature", "electric", "shadow", "ice", "psychic", "normal"):
        assert ws.get_damage_modifier(move_type) == 1.0


# ---------------------------------------------------------------------------
# tick
# ---------------------------------------------------------------------------

def test_tick_decrements_turns_remaining():
    ws = WeatherSystem()
    ws.current = "Rainy"
    ws.turns_remaining = 3
    result = ws.tick()
    assert ws.turns_remaining == 2
    assert result is None  # weather didn't change yet


def test_tick_rolls_new_weather_when_turns_reach_zero():
    ws = WeatherSystem()
    ws.current = "Rainy"
    ws.turns_remaining = 1
    result = ws.tick()
    # After tick, turns_remaining reached 0, so new weather was rolled
    assert result is not None
    assert result in WEATHER_CONDITIONS
    assert ws.turns_remaining >= 3


# ---------------------------------------------------------------------------
# Serialization round-trip
# ---------------------------------------------------------------------------

def test_to_dict_from_dict_round_trip():
    ws = WeatherSystem()
    ws.current = "Stormy"
    ws.turns_remaining = 4

    data = ws.to_dict()
    ws2 = WeatherSystem.from_dict(data)
    assert ws2.current == "Stormy"
    assert ws2.turns_remaining == 4
