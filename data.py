"""Game data: type chart, starter creatures, moves, and encounter tables."""
from __future__ import annotations

from creature import Move

# -- Type advantage chart --
# Maps attacker_type -> set of types it is strong against.
# Symmetric rule: if A is strong vs B, then B resists A.
TYPE_CHART: dict[str, set[str]] = {
    "fire":     {"nature"},
    "water":    {"fire"},
    "nature":   {"water"},
    "electric": {"water"},
    "shadow":   {"electric"},
}

WEAKNESS_MULTIPLIER = 1.5
RESISTANCE_MULTIPLIER = 0.5

# -- Moves --
MOVE_POOL: dict[str, list[Move]] = {
    "fire": [
        Move("Ember", "fire", 6, "A small burst of flames"),
        Move("Blaze Rush", "fire", 9, "Charge forward wreathed in fire"),
    ],
    "water": [
        Move("Splash Strike", "water", 6, "A jet of pressurized water"),
        Move("Tidal Slam", "water", 9, "A crashing wave of force"),
    ],
    "nature": [
        Move("Vine Whip", "nature", 6, "Lash out with thorny vines"),
        Move("Leaf Storm", "nature", 9, "A whirlwind of razor leaves"),
    ],
    "electric": [
        Move("Spark", "electric", 6, "A quick zap of static"),
        Move("Thunder Bolt", "electric", 9, "A powerful lightning strike"),
    ],
    "shadow": [
        Move("Dark Pulse", "shadow", 6, "A wave of shadowy energy"),
        Move("Nightmare", "shadow", 9, "Engulf the foe in darkness"),
    ],
    "normal": [
        Move("Tackle", "normal", 5, "A basic body slam"),
        Move("Headbutt", "normal", 7, "A solid headbutt"),
    ],
}

# -- Starter creature templates --
# Each entry: (name, creature_type, base_level, move_keys)
STARTER_CREATURES: list[dict] = [
    # Fire
    {"name": "Blazepup",   "creature_type": "fire",     "level": 1,
     "moves": ["fire", "normal"]},
    {"name": "Cinderax",   "creature_type": "fire",     "level": 1,
     "moves": ["fire", "normal"]},
    # Water
    {"name": "Aquafin",    "creature_type": "water",    "level": 1,
     "moves": ["water", "normal"]},
    {"name": "Tidalynx",   "creature_type": "water",    "level": 1,
     "moves": ["water", "normal"]},
    # Nature
    {"name": "Thornwhip",  "creature_type": "nature",   "level": 1,
     "moves": ["nature", "normal"]},
    {"name": "Mossling",   "creature_type": "nature",   "level": 1,
     "moves": ["nature", "normal"]},
    # Electric
    {"name": "Zappaw",     "creature_type": "electric", "level": 1,
     "moves": ["electric", "normal"]},
    {"name": "Voltfox",    "creature_type": "electric", "level": 1,
     "moves": ["electric", "normal"]},
    # Shadow
    {"name": "Duskfang",   "creature_type": "shadow",   "level": 1,
     "moves": ["shadow", "normal"]},
    {"name": "Gloomwing",  "creature_type": "shadow",   "level": 1,
     "moves": ["shadow", "normal"]},
]

def get_moves_for_types(type_keys: list[str]) -> list[Move]:
    """Return the first move from each requested type pool."""
    moves = []
    for key in type_keys:
        pool = MOVE_POOL.get(key, [])
        if pool:
            moves.append(pool[0])
    return moves

# -- Encounter tables --
# Maps area name -> list of (creature_template_index, min_level, max_level)
ENCOUNTER_TABLES: dict[str, list[dict]] = {
    "Scorched Plains": [
        {"template": 0, "min_level": 1, "max_level": 3},
        {"template": 1, "min_level": 2, "max_level": 4},
    ],
    "Crystal Lake": [
        {"template": 2, "min_level": 1, "max_level": 3},
        {"template": 3, "min_level": 2, "max_level": 4},
    ],
    "Whispering Woods": [
        {"template": 4, "min_level": 1, "max_level": 3},
        {"template": 5, "min_level": 2, "max_level": 4},
    ],
    "Thunder Peak": [
        {"template": 6, "min_level": 1, "max_level": 3},
        {"template": 7, "min_level": 2, "max_level": 4},
    ],
    "Shadow Caverns": [
        {"template": 8, "min_level": 2, "max_level": 5},
        {"template": 9, "min_level": 3, "max_level": 5},
    ],
}

# -- ASCII art for creatures (simple, kid-friendly) --
CREATURE_ART: dict[str, str] = {
    "Blazepup":  r"""
   /\  /\
  ( o  o )~🔥
   > ^^ <
  /|    |\
""",
    "Cinderax":  r"""
    /\_/\
   ( . . ) 🔥
    > ~ <
   _|   |_
""",
    "Aquafin":   r"""
     ><>
   ><(((°> 💧
     ><>
""",
    "Tidalynx":  r"""
   /\___/\
  ( o . o ) 💧
   / > < \
""",
    "Thornwhip": r"""
   \|/
  --*-- 🌿
   /|\
  / | \
""",
    "Mossling":  r"""
   (  )
  (    ) 🌿
   \  /
    \/
""",
    "Zappaw":    r"""
   /\  /\
  ( ⚡ ⚡)
   > vv <
    |  |
""",
    "Voltfox":   r"""
   /\_/\  ⚡
  ( ^ ^ )
   \   /
    \_/
""",
    "Duskfang":  r"""
   /\  /\
  ( 🌙  ) 
   >    <
   |    |
""",
    "Gloomwing": r"""
  .-~~~-.
 / 🌙🌙 \
(  ~~~~  )
 \      /
""",
}
