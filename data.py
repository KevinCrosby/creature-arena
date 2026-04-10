"""Game data: type chart, starter creatures, moves, and encounter tables."""
from __future__ import annotations

from creature import Move

# -- Type advantage chart --
# Maps attacker_type -> set of types it is strong against.
# Symmetric rule: if A is strong vs B, then B resists A.
TYPE_CHART: dict[str, set[str]] = {
    "fire":     {"nature", "ice"},
    "water":    {"fire"},
    "nature":   {"water", "electric"},
    "electric": {"water"},
    "shadow":   {"electric", "psychic"},
    "ice":      {"nature", "shadow"},
    "psychic":  {"shadow"},
}

WEAKNESS_MULTIPLIER = 1.5
RESISTANCE_MULTIPLIER = 0.5

# -- Moves --
MOVE_POOL: dict[str, list[Move]] = {
    "fire": [
        Move("Ember", "fire", 6, "A small burst of flames"),
        Move("Blaze Rush", "fire", 9, "Charge forward wreathed in fire"),
        Move("Scorch", "fire", 4, "Searing flames that burn", effect="burn", effect_chance=0.4, effect_duration=3),
    ],
    "water": [
        Move("Splash Strike", "water", 6, "A jet of pressurized water"),
        Move("Tidal Slam", "water", 9, "A crashing wave of force"),
        Move("Aqua Shield", "water", 0, "A protective water barrier", effect="shield", effect_chance=1.0, effect_duration=2),
    ],
    "nature": [
        Move("Vine Whip", "nature", 6, "Lash out with thorny vines"),
        Move("Leaf Storm", "nature", 9, "A whirlwind of razor leaves"),
        Move("Toxic Spore", "nature", 3, "Releases poisonous spores", effect="poison", effect_chance=0.5, effect_duration=3),
    ],
    "electric": [
        Move("Spark", "electric", 6, "A quick zap of static"),
        Move("Thunder Bolt", "electric", 9, "A powerful lightning strike"),
        Move("Static Shock", "electric", 4, "A paralyzing jolt", effect="stun", effect_chance=0.35, effect_duration=1),
    ],
    "shadow": [
        Move("Dark Pulse", "shadow", 6, "A wave of shadowy energy"),
        Move("Nightmare", "shadow", 9, "Engulf the foe in darkness"),
        Move("Shadow Curse", "shadow", 3, "A dark curse that poisons", effect="poison", effect_chance=0.45, effect_duration=3),
    ],
    "normal": [
        Move("Tackle", "normal", 5, "A basic body slam"),
        Move("Headbutt", "normal", 7, "A solid headbutt"),
        Move("Power Up", "normal", 0, "Channel inner strength", effect="boost", effect_chance=1.0, effect_duration=3),
    ],
    "ice": [
        Move("Frost Bite", "ice", 6, "A freezing chomp"),
        Move("Blizzard", "ice", 9, "A howling ice storm"),
        Move("Freeze Ray", "ice", 4, "A ray that may stun", effect="stun", effect_chance=0.3, effect_duration=1),
    ],
    "psychic": [
        Move("Mind Blast", "psychic", 6, "A wave of psychic force"),
        Move("Hypnosis", "psychic", 3, "Mesmerizing stare", effect="stun", effect_chance=0.5, effect_duration=2),
        Move("Psychic Shield", "psychic", 0, "Mental barrier", effect="shield", effect_chance=1.0, effect_duration=2),
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

# -- Evolution chains --
# Maps creature name -> evolution info (level threshold, evolved form, stat bonus, new move types)
EVOLUTION_CHAINS: dict[str, dict] = {
    # Fire evolutions
    "Blazepup": {"level": 5, "evolves_to": "Infernohound", "stat_bonus": 5,
                 "new_moves": ["fire"]},
    "Infernohound": {"level": 10, "evolves_to": "Pyraking", "stat_bonus": 8,
                     "new_moves": ["fire"]},
    "Cinderax": {"level": 5, "evolves_to": "Blazeclaw", "stat_bonus": 5,
                 "new_moves": ["fire"]},
    # Water evolutions
    "Aquafin": {"level": 5, "evolves_to": "Tidalstrike", "stat_bonus": 5,
                "new_moves": ["water"]},
    "Tidalstrike": {"level": 10, "evolves_to": "Tsunamirex", "stat_bonus": 8,
                    "new_moves": ["water"]},
    "Tidalynx": {"level": 5, "evolves_to": "Oceanlynx", "stat_bonus": 5,
                 "new_moves": ["water"]},
    # Nature evolutions
    "Thornwhip": {"level": 5, "evolves_to": "Briarfury", "stat_bonus": 5,
                  "new_moves": ["nature"]},
    "Briarfury": {"level": 10, "evolves_to": "Thornlord", "stat_bonus": 8,
                  "new_moves": ["nature"]},
    "Mossling": {"level": 5, "evolves_to": "Mossguard", "stat_bonus": 5,
                 "new_moves": ["nature"]},
    # Electric evolutions
    "Zappaw": {"level": 5, "evolves_to": "Thunderclaw", "stat_bonus": 5,
               "new_moves": ["electric"]},
    "Thunderclaw": {"level": 10, "evolves_to": "Stormfang", "stat_bonus": 8,
                    "new_moves": ["electric"]},
    "Voltfox": {"level": 5, "evolves_to": "Lightningfox", "stat_bonus": 5,
                "new_moves": ["electric"]},
    # Shadow evolutions
    "Duskfang": {"level": 5, "evolves_to": "Nightterror", "stat_bonus": 5,
                 "new_moves": ["shadow"]},
    "Nightterror": {"level": 10, "evolves_to": "Voidreaper", "stat_bonus": 8,
                    "new_moves": ["shadow"]},
    "Gloomwing": {"level": 5, "evolves_to": "Shadowraven", "stat_bonus": 5,
                  "new_moves": ["shadow"]},
}

def get_moves_for_types(type_keys: list[str], tier: int = 0) -> list[Move]:
    """Return moves from each type pool. tier=0 gives first move, tier=1 gives second, etc."""
    moves = []
    for key in type_keys:
        pool = MOVE_POOL.get(key, [])
        idx = min(tier, len(pool) - 1) if pool else 0
        if pool:
            moves.append(pool[idx])
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
    "Frozen Tundra": [
        {"template": 0, "min_level": 5, "max_level": 8},
        {"template": 2, "min_level": 5, "max_level": 8},
        {"template": 8, "min_level": 5, "max_level": 8},
    ],
    "Mystic Ruins": [
        {"template": 6, "min_level": 4, "max_level": 7},
        {"template": 9, "min_level": 4, "max_level": 7},
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
    # -- Evolved forms: Fire --
    "Infernohound": r"""
     /\  /\
    (💥  💥)~🔥🔥
     > WW <
    /|    |\
   / |    | \
""",
    "Pyraking": r"""
       👑
      /\  /\
     (🔥  🔥)
      > WW <
    /||    ||\
   / ||    || \
     ||    ||
""",
    "Blazeclaw": r"""
      /\  /\
     ( 🔥 🔥)
      >  ~ <  🔥
     /| __ |\
    / |/  \| \
""",
    # -- Evolved forms: Water --
    "Tidalstrike": r"""
       __
     ><((°>  💧💧
    ><(((°>
     ><((°>
       ~~
""",
    "Tsunamirex": r"""
      ___  🌊🌊
    ><((((°>
   ><(((((°>  💧
    ><((((°>
      ~~~
     ~~~~~
""",
    "Oceanlynx": r"""
     /\___/\
    ( 💧 💧 )  🌊
     / >w< \
    /|      |\
   / |      | \
""",
    # -- Evolved forms: Nature --
    "Briarfury": r"""
    \|/ \|/
   --***-- 🌿🌿
    /|\ /|\
   / | X | \
     | | |
""",
    "Thornlord": r"""
   \|/\|/\|/
  --*****-- 🌿🌿🌿
   /|/|\||\
  / || || | \
    || || ||
    || || ||
""",
    "Mossguard": r"""
    (    )
   ( 🌿🌿 )
  (        )
   \  /\  /
    \/  \/
""",
    # -- Evolved forms: Electric --
    "Thunderclaw": r"""
     /\  /\  ⚡⚡
    ( ⚡  ⚡)
     > VV <
    /|    |\
   / |    | \
""",
    "Stormfang": r"""
   ⚡⚡  ⚡⚡
     /\  /\
    ( ⚡  ⚡)
     > VV <
   //|    |\\
  / /|    |\ \
    /|    |\
""",
    "Lightningfox": r"""
     /\_/\  ⚡⚡
    ( ⚡ ⚡ )
     \ ~ /
    /|   |\
   / |   | \
""",
    # -- Evolved forms: Shadow --
    "Nightterror": r"""
     /\  /\
    (👁  👁) 🌑🌑
     > ~~ <
    /|    |\
   / |    | \
     |    |
""",
    "Voidreaper": r"""
   🌑  /\  /\  🌑
     (👁  👁)
      > ~~ <
    //|    |\\
   / /|    |\ \
    / |    | \
      |    |
""",
    "Shadowraven": r"""
    .-~===~-.
   / 👁  👁  \ 🌑
  (  ~~~~~~  )
   \  ~~~~  /
    '-.=.-'
""",
}
