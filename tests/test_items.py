from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from items import Inventory, get_shop_items
from creature import Creature, Move
from data import ITEMS


# ---------------------------------------------------------------------------
# Basic inventory state
# ---------------------------------------------------------------------------

def test_inventory_starts_with_100_gold_and_empty_items():
    inv = Inventory()
    assert inv.gold == 100
    assert inv.items == {}


def test_inventory_custom_gold():
    inv = Inventory(gold=250)
    assert inv.gold == 250


# ---------------------------------------------------------------------------
# add / remove / has / get_quantity
# ---------------------------------------------------------------------------

def test_add_item_increases_quantity():
    inv = Inventory()
    inv.add_item("Potion", 3)
    assert inv.get_quantity("Potion") == 3


def test_add_item_stacks():
    inv = Inventory()
    inv.add_item("Potion", 2)
    inv.add_item("Potion", 1)
    assert inv.get_quantity("Potion") == 3


def test_remove_item_decreases_quantity():
    inv = Inventory()
    inv.add_item("Potion", 2)
    assert inv.remove_item("Potion") is True
    assert inv.get_quantity("Potion") == 1


def test_remove_item_deletes_at_zero():
    inv = Inventory()
    inv.add_item("Potion", 1)
    inv.remove_item("Potion")
    assert inv.has_item("Potion") is False
    assert inv.get_quantity("Potion") == 0


def test_remove_item_returns_false_when_missing():
    inv = Inventory()
    assert inv.remove_item("Potion") is False


def test_has_item():
    inv = Inventory()
    assert inv.has_item("Potion") is False
    inv.add_item("Potion")
    assert inv.has_item("Potion") is True


# ---------------------------------------------------------------------------
# buy_item
# ---------------------------------------------------------------------------

def test_buy_item_deducts_gold():
    inv = Inventory(gold=100)
    assert inv.buy_item("Potion") is True
    assert inv.gold == 100 - ITEMS["Potion"]["price"]
    assert inv.has_item("Potion") is True


def test_buy_item_fails_when_cant_afford():
    inv = Inventory(gold=0)
    assert inv.buy_item("Potion") is False
    assert inv.has_item("Potion") is False


def test_buy_item_fails_for_unknown_item():
    inv = Inventory(gold=9999)
    assert inv.buy_item("Nonexistent Widget") is False


# ---------------------------------------------------------------------------
# use_item — heal
# ---------------------------------------------------------------------------

def _make_creature(hp=10, max_hp=50, **kwargs):
    c = Creature("TestMon", "fire", level=5, moves=[Move("Tackle", "normal", 5)])
    c.max_hp = max_hp
    c.hp = hp
    for k, v in kwargs.items():
        setattr(c, k, v)
    return c


def test_use_item_heal_restores_hp():
    inv = Inventory()
    inv.add_item("Potion")
    c = _make_creature(hp=10, max_hp=50)
    ok, msg = inv.use_item("Potion", c)
    assert ok is True
    assert c.hp == 30  # 10 + 20
    assert "healed" in msg.lower() or "HP" in msg


def test_use_item_heal_caps_at_max_hp():
    inv = Inventory()
    inv.add_item("Potion")
    c = _make_creature(hp=45, max_hp=50)
    ok, _ = inv.use_item("Potion", c)
    assert ok is True
    assert c.hp == 50


def test_use_item_heal_rejected_at_full_hp():
    inv = Inventory()
    inv.add_item("Potion")
    c = _make_creature(hp=50, max_hp=50)
    ok, msg = inv.use_item("Potion", c)
    assert ok is False
    assert inv.has_item("Potion")  # item not consumed


# ---------------------------------------------------------------------------
# use_item — full_heal
# ---------------------------------------------------------------------------

def test_use_item_full_heal():
    inv = Inventory()
    inv.add_item("Full Heal")
    c = _make_creature(hp=1, max_hp=50)
    c.apply_status("poison", 3)
    ok, msg = inv.use_item("Full Heal", c)
    assert ok is True
    assert c.hp == c.max_hp
    assert c.status_effects == {}


# ---------------------------------------------------------------------------
# use_item — cure_status
# ---------------------------------------------------------------------------

def test_use_item_cure_status():
    inv = Inventory()
    inv.add_item("Antidote")
    c = _make_creature()
    c.apply_status("poison", 3)
    c.apply_status("burn", 2)
    ok, _ = inv.use_item("Antidote", c)
    assert ok is True
    assert c.status_effects == {}


# ---------------------------------------------------------------------------
# use_item — stat_boost
# ---------------------------------------------------------------------------

def test_use_item_stat_boost():
    inv = Inventory()
    inv.add_item("Attack Berry")
    c = _make_creature()
    old_attack = c.attack
    ok, msg = inv.use_item("Attack Berry", c)
    assert ok is True
    assert c.attack == old_attack + ITEMS["Attack Berry"]["value"]


# ---------------------------------------------------------------------------
# use_item — catch_boost / xp_boost
# ---------------------------------------------------------------------------

def test_use_item_catch_boost():
    inv = Inventory()
    inv.add_item("Capture Stone")
    c = _make_creature()
    ok, _ = inv.use_item("Capture Stone", c)
    assert ok is True
    assert inv.active_catch_boost == ITEMS["Capture Stone"]["value"]


def test_use_item_xp_boost():
    inv = Inventory()
    inv.add_item("XP Charm")
    c = _make_creature()
    ok, _ = inv.use_item("XP Charm", c)
    assert ok is True
    assert inv.active_xp_boost == ITEMS["XP Charm"]["value"]


# ---------------------------------------------------------------------------
# consume_catch_boost / consume_xp_boost
# ---------------------------------------------------------------------------

def test_consume_catch_boost_returns_and_resets():
    inv = Inventory()
    inv.active_catch_boost = 0.5
    val = inv.consume_catch_boost()
    assert val == 0.5
    assert inv.active_catch_boost == 0.0


def test_consume_xp_boost_returns_and_resets():
    inv = Inventory()
    inv.active_xp_boost = 2.0
    val = inv.consume_xp_boost()
    assert val == 2.0
    assert inv.active_xp_boost == 1.0


# ---------------------------------------------------------------------------
# Serialization round-trip
# ---------------------------------------------------------------------------

def test_to_dict_from_dict_round_trip():
    inv = Inventory(gold=42)
    inv.add_item("Potion", 3)
    inv.add_item("Antidote", 1)
    inv.active_xp_boost = 1.5
    inv.active_catch_boost = 0.3

    data = inv.to_dict()
    inv2 = Inventory.from_dict(data)
    assert inv2.gold == 42
    assert inv2.get_quantity("Potion") == 3
    assert inv2.get_quantity("Antidote") == 1
    assert inv2.active_xp_boost == 1.5
    assert inv2.active_catch_boost == 0.3


# ---------------------------------------------------------------------------
# get_shop_items
# ---------------------------------------------------------------------------

def test_get_shop_items_returns_non_empty_list():
    items = get_shop_items()
    assert isinstance(items, list)
    assert len(items) > 0
    name, data = items[0]
    assert isinstance(name, str)
    assert "price" in data
