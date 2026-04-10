"""Item and inventory system for creature management."""
from __future__ import annotations


class Inventory:
    """Player inventory with items, gold, and active boosts."""

    def __init__(self, gold: int = 100) -> None:
        self.gold: int = gold
        self.items: dict[str, int] = {}
        self.active_xp_boost: float = 1.0
        self.active_catch_boost: float = 0.0

    # -- Basic item operations --

    def add_item(self, name: str, qty: int = 1) -> None:
        self.items[name] = self.items.get(name, 0) + qty

    def remove_item(self, name: str) -> bool:
        if self.items.get(name, 0) <= 0:
            return False
        self.items[name] -= 1
        if self.items[name] <= 0:
            del self.items[name]
        return True

    def has_item(self, name: str) -> bool:
        return self.items.get(name, 0) > 0

    def get_quantity(self, name: str) -> int:
        return self.items.get(name, 0)

    # -- Using items --

    def use_item(self, name: str, creature) -> tuple[bool, str]:
        """Use an item on a creature. Returns (success, message)."""
        from data import ITEMS

        if not self.has_item(name):
            return False, f"You don't have any {name}."

        if name not in ITEMS:
            return False, f"Unknown item: {name}"

        item = ITEMS[name]
        item_type = item["type"]

        if item_type == "heal":
            if creature.hp >= creature.max_hp:
                return False, f"{creature.name} is already at full HP."
            old_hp = creature.hp
            creature.hp = min(creature.hp + item["value"], creature.max_hp)
            self.remove_item(name)
            return True, f"{creature.name} healed {creature.hp - old_hp} HP."

        if item_type == "full_heal":
            creature.heal()
            self.remove_item(name)
            return True, f"{creature.name} fully restored!"

        if item_type == "cure_status":
            creature.clear_statuses()
            self.remove_item(name)
            return True, f"{creature.name}'s status effects cleared!"

        if item_type == "stat_boost":
            stat = item["stat"]
            value = item["value"]
            current = getattr(creature, stat)
            setattr(creature, stat, current + value)
            self.remove_item(name)
            return True, f"{creature.name}'s {stat} increased by {value}!"

        if item_type == "catch_boost":
            self.active_catch_boost += item["value"]
            self.remove_item(name)
            return True, f"Catch boost active! (+{item['value'] * 100:.0f}%)"

        if item_type == "xp_boost":
            self.active_xp_boost = item["value"]
            self.remove_item(name)
            return True, f"XP boost active! ({item['value']}x)"

        return False, f"Unknown item type: {item_type}"

    # -- Shop --

    def buy_item(self, name: str) -> bool:
        """Buy an item from the shop. Returns False if can't afford."""
        from data import ITEMS

        if name not in ITEMS:
            return False
        price = ITEMS[name]["price"]
        if self.gold < price:
            return False
        self.gold -= price
        self.add_item(name)
        return True

    # -- Boost consumption --

    def consume_catch_boost(self) -> float:
        boost = self.active_catch_boost
        self.active_catch_boost = 0.0
        return boost

    def consume_xp_boost(self) -> float:
        boost = self.active_xp_boost
        self.active_xp_boost = 1.0
        return boost

    # -- Serialization --

    def to_dict(self) -> dict:
        return {
            "gold": self.gold,
            "items": dict(self.items),
            "active_xp_boost": self.active_xp_boost,
            "active_catch_boost": self.active_catch_boost,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Inventory:
        inv = cls(gold=data.get("gold", 100))
        inv.items = data.get("items", {})
        inv.active_xp_boost = data.get("active_xp_boost", 1.0)
        inv.active_catch_boost = data.get("active_catch_boost", 0.0)
        return inv


def get_shop_items() -> list[tuple[str, dict]]:
    """Return list of (name, item_data) for all shop items."""
    from data import ITEMS
    return list(ITEMS.items())
