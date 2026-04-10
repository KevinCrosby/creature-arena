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
    effect: str | None = None
    effect_chance: float = 0.0
    effect_duration: int = 0


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
        secondary_type: str | None = None,
        ability: str | None = None,
        nickname: str | None = None,
    ):
        self.name = name
        self.creature_type = creature_type
        self.secondary_type = secondary_type
        self.ability = ability
        self.nickname = nickname
        self.level = max(1, level)
        self.max_hp = 20 + (self.level * 5)
        self.hp = hp if hp is not None else self.max_hp
        self.hp = max(0, min(self.hp, self.max_hp))
        self.attack = 5 + (self.level * 2)
        self.defense = 3 + self.level
        self.xp = max(0, xp)
        self.xp_to_next = self.level * 10
        self.moves: list[Move] = moves if moves is not None else []
        self.speed = 4 + self.level
        self.status_effects: dict[str, int] = {}
        self.evolution_stage: int = 0
        self.is_defending: bool = False

    @property
    def display_name(self) -> str:
        """Return nickname if set, otherwise species name."""
        return self.nickname if self.nickname else self.name

    @property
    def types(self) -> list[str]:
        """Return list of all types (primary + secondary if present)."""
        if self.secondary_type:
            return [self.creature_type, self.secondary_type]
        return [self.creature_type]

    # -- Status effects --

    def apply_status(self, effect: str, duration: int) -> bool:
        """Apply a status effect. Returns True if newly applied (not already active)."""
        if effect in self.status_effects:
            return False
        self.status_effects[effect] = duration
        return True

    def tick_statuses(self) -> list[tuple[str, int]]:
        """Process status effects at start of turn. Returns list of (effect, damage_dealt)."""
        results = []
        expired = []
        for effect, turns in self.status_effects.items():
            damage = 0
            if effect == "poison":
                damage = max(1, self.max_hp // 8)
                self.hp = max(0, self.hp - damage)
            elif effect == "burn":
                damage = max(1, self.max_hp // 6)
                self.hp = max(0, self.hp - damage)
            results.append((effect, damage))
            if turns <= 1:
                expired.append(effect)
            else:
                self.status_effects[effect] = turns - 1
        for e in expired:
            del self.status_effects[e]
        return results

    def is_stunned(self) -> bool:
        """Check if creature is stunned (skips turn)."""
        return "stun" in self.status_effects

    def has_shield(self) -> bool:
        return "shield" in self.status_effects

    def has_boost(self) -> bool:
        return "boost" in self.status_effects

    def get_effective_attack(self) -> int:
        """Attack with boost modifier applied."""
        base = self.attack
        if self.has_boost():
            base = int(base * 1.5)
        return base

    def get_effective_defense(self) -> int:
        """Defense with shield/defend modifiers."""
        base = self.defense
        if self.has_shield():
            base = int(base * 1.5)
        if self.is_defending:
            base *= 2
        return base

    def clear_statuses(self) -> None:
        """Remove all status effects."""
        self.status_effects.clear()
        self.is_defending = False

    # -- Combat --

    def take_damage(self, raw_amount: int) -> int:
        """Apply damage after defense. Returns actual damage dealt (always >= 1)."""
        actual = max(1, raw_amount - self.get_effective_defense())
        self.hp = max(0, self.hp - actual)
        self.is_defending = False
        return actual

    def is_fainted(self) -> bool:
        return self.hp <= 0

    def heal(self) -> None:
        """Fully restore HP and clear status effects."""
        self.hp = self.max_hp
        self.clear_statuses()

    # -- Progression --

    def gain_xp(self, amount: int) -> tuple[bool, str | None]:
        """Add XP. Returns (leveled_up, evolved_to_name_or_None)."""
        if amount <= 0:
            return False, None
        self.xp += amount
        if self.xp >= self.xp_to_next:
            self._level_up()
            # Check for autonomous evolution
            from evolution import evolve_creature
            new_name = evolve_creature(self)
            return True, new_name
        return False, None

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
        self.speed = 4 + self.level
        self.xp_to_next = self.level * 10

    def evolve(self, new_name: str, new_moves: list[Move] | None = None, stat_bonus: int = 5) -> None:
        """Transform this creature into its evolved form."""
        self.name = new_name
        self.evolution_stage += 1
        self.max_hp += stat_bonus
        self.hp = min(self.hp + stat_bonus, self.max_hp)
        self.attack += stat_bonus // 2
        self.defense += stat_bonus // 3
        self.speed += 1
        if new_moves:
            self.moves.extend(new_moves)

    # -- Serialization --

    def to_dict(self) -> dict:
        """Serialize to a JSON-safe dictionary."""
        d: dict = {
            "name": self.name,
            "creature_type": self.creature_type,
            "level": self.level,
            "hp": self.hp,
            "xp": self.xp,
            "moves": [
                {"name": m.name, "move_type": m.move_type,
                 "power": m.power, "description": m.description,
                 "effect": m.effect, "effect_chance": m.effect_chance,
                 "effect_duration": m.effect_duration}
                for m in self.moves
            ],
            "speed": self.speed,
            "status_effects": dict(self.status_effects),
            "evolution_stage": self.evolution_stage,
        }
        if self.secondary_type:
            d["secondary_type"] = self.secondary_type
        if self.ability:
            d["ability"] = self.ability
        if self.nickname:
            d["nickname"] = self.nickname
        return d

    @classmethod
    def from_dict(cls, data: dict) -> Creature:
        """Deserialize from a dictionary."""
        moves = [
            Move(
                name=m["name"],
                move_type=m["move_type"],
                power=m["power"],
                description=m.get("description", ""),
                effect=m.get("effect"),
                effect_chance=m.get("effect_chance", 0.0),
                effect_duration=m.get("effect_duration", 0),
            )
            for m in data.get("moves", [])
        ]
        creature = cls(
            name=data["name"],
            creature_type=data["creature_type"],
            level=data.get("level", 1),
            moves=moves,
            xp=data.get("xp", 0),
            hp=data.get("hp"),
            secondary_type=data.get("secondary_type"),
            ability=data.get("ability"),
            nickname=data.get("nickname"),
        )
        creature.status_effects = data.get("status_effects", {})
        creature.evolution_stage = data.get("evolution_stage", 0)
        if "speed" in data:
            creature.speed = data["speed"]
        return creature

    def __repr__(self) -> str:
        return f"Creature({self.name!r}, type={self.creature_type}, lv={self.level}, hp={self.hp}/{self.max_hp})"
