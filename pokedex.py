from __future__ import annotations

from data import STARTER_CREATURES


class Pokedex:
    """Creature journal tracking seen, caught, and areas visited."""

    def __init__(self) -> None:
        self.seen: set[str] = set()
        self.caught: set[str] = set()
        self.areas_visited: set[str] = set()

    # -- Mutators ----------------------------------------------------------

    def mark_seen(self, name: str) -> None:
        self.seen.add(name)

    def mark_caught(self, name: str) -> None:
        self.seen.add(name)
        self.caught.add(name)

    def mark_area(self, area: str) -> None:
        self.areas_visited.add(area)

    # -- Queries -----------------------------------------------------------

    def is_seen(self, name: str) -> bool:
        return name in self.seen

    def is_caught(self, name: str) -> bool:
        return name in self.caught

    def get_completion_rate(self) -> float:
        total = len({c["name"] for c in STARTER_CREATURES})
        if total == 0:
            return 0.0
        return len(self.caught) / total

    def get_seen_count(self) -> int:
        return len(self.seen)

    def get_caught_count(self) -> int:
        return len(self.caught)

    def get_summary(self) -> str:
        total = len({c["name"] for c in STARTER_CREATURES})
        pct = int(self.get_completion_rate() * 100)
        return (
            f"\U0001f4d6 Pokédex: {self.get_seen_count()}/{total} seen, "
            f"{self.get_caught_count()}/{total} caught ({pct}%)"
        )

    # -- Serialisation -----------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "seen": sorted(self.seen),
            "caught": sorted(self.caught),
            "areas_visited": sorted(self.areas_visited),
        }

    @classmethod
    def from_dict(cls, data: dict) -> Pokedex:
        dex = cls()
        dex.seen = set(data.get("seen", []))
        dex.caught = set(data.get("caught", []))
        dex.areas_visited = set(data.get("areas_visited", []))
        return dex
