"""Weather system that modifies battle conditions."""
from __future__ import annotations

import random


class WeatherSystem:
    """Tracks weather conditions and applies damage modifiers."""

    def __init__(self) -> None:
        self.current: str = "Clear"
        self.turns_remaining: int = 0

    def roll_weather(self) -> str:
        """Randomly select a new weather condition (weighted)."""
        from data import WEATHER_CONDITIONS

        weathers = list(WEATHER_CONDITIONS.keys())
        weights = [40 if w == "Clear" else 10 for w in weathers]
        self.current = random.choices(weathers, weights=weights, k=1)[0]
        self.turns_remaining = random.randint(3, 5)
        return self.current

    def get_description(self) -> str:
        """Return the description string for the current weather."""
        from data import WEATHER_CONDITIONS
        return WEATHER_CONDITIONS[self.current]["description"]

    def get_damage_modifier(self, move_type: str) -> float:
        """Return damage multiplier for a move type under current weather."""
        from data import WEATHER_CONDITIONS, WEATHER_BOOST, WEATHER_WEAKEN

        condition = WEATHER_CONDITIONS[self.current]
        if move_type in condition["boosts"]:
            return WEATHER_BOOST
        if move_type in condition["weakens"]:
            return WEATHER_WEAKEN
        return 1.0

    def tick(self) -> str | None:
        """Advance one turn. Returns new weather name if it changed, else None."""
        if self.turns_remaining > 0:
            self.turns_remaining -= 1
        if self.turns_remaining <= 0:
            old = self.current
            self.roll_weather()
            if self.current != old:
                return self.current
            return self.current  # still report even if same weather re-rolled
        return None

    # -- Serialization --

    def to_dict(self) -> dict:
        return {
            "current": self.current,
            "turns_remaining": self.turns_remaining,
        }

    @classmethod
    def from_dict(cls, data: dict) -> WeatherSystem:
        ws = cls()
        ws.current = data.get("current", "Clear")
        ws.turns_remaining = data.get("turns_remaining", 0)
        return ws
