"""Creature and Move data classes with stat calculations and leveling."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Move:
    """A combat move a creature can use."""
    name: str
    move_type: str  # "fire", "water", "nature", "electric", "shadow", "normal"
    power: int
    description: str = ""


class Creature:
    """A collectible creature with stats, moves, and leveling."""

    def __init__(
        self,
        name: str,
        creature_type: str,
        level: int = 1,
        moves: list[Move] | None = None,
        xp: int = 0,
        hp: int | None = None,
    ):
        self.name = name
        self.creature_type = creature_type
        self.level = max(1, level)
        self.max_hp = 20 + (self.level * 5)
        self.hp = hp if hp is not None else self.max_hp
        self.hp = max(0, min(self.hp, self.max_hp))
        self.attack = 5 + (self.level * 2)
        self.defense = 3 + self.level
        self.xp = max(0, xp)
        self.xp_to_next = self.level * 10
        self.moves: list[Move] = moves if moves is not None else []

    # -- Combat --

    def take_damage(self, raw_amount: int) -> int:
        """Apply damage after defense. Returns actual damage dealt (always >= 1)."""
        actual = max(1, raw_amount - self.defense)
        self.hp = max(0, self.hp - actual)
        return actual

    def is_fainted(self) -> bool:
        return self.hp <= 0

    def heal(self) -> None:
        """Fully restore HP."""
        self.hp = self.max_hp

    # -- Progression --

    def gain_xp(self, amount: int) -> bool:
        """Add XP. Returns True if leveled up."""
        if amount <= 0:
            return False
        self.xp += amount
        if self.xp >= self.xp_to_next:
            self._level_up()
            return True
        return False

    def _level_up(self) -> None:
        """Advance one level and recalculate stats."""
        self.xp -= self.xp_to_next
        self.level += 1
        old_max = self.max_hp
        self.max_hp = 20 + (self.level * 5)
        self.hp += self.max_hp - old_max  # Gain the HP difference
        self.hp = min(self.hp, self.max_hp)
        self.attack = 5 + (self.level * 2)
        self.defense = 3 + self.level
        self.xp_to_next = self.level * 10

    # -- Serialization --

    def to_dict(self) -> dict:
        """Serialize to a JSON-safe dictionary."""
        return {
            "name": self.name,
            "creature_type": self.creature_type,
            "level": self.level,
            "hp": self.hp,
            "xp": self.xp,
            "moves": [
                {"name": m.name, "move_type": m.move_type,
                 "power": m.power, "description": m.description}
                for m in self.moves
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Creature:
        """Deserialize from a dictionary."""
        moves = [
            Move(
                name=m["name"],
                move_type=m["move_type"],
                power=m["power"],
                description=m.get("description", ""),
            )
            for m in data.get("moves", [])
        ]
        return cls(
            name=data["name"],
            creature_type=data["creature_type"],
            level=data.get("level", 1),
            moves=moves,
            xp=data.get("xp", 0),
            hp=data.get("hp"),
        )

    def __repr__(self) -> str:
        return f"Creature({self.name!r}, type={self.creature_type}, lv={self.level}, hp={self.hp}/{self.max_hp})"
