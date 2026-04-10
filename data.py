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
    # Ice
    {"name": "Frostpaw",   "creature_type": "ice",      "level": 1,
     "moves": ["ice", "normal"]},
    {"name": "Glacimole",  "creature_type": "ice",      "level": 1,
     "moves": ["ice", "normal"]},
    # Psychic
    {"name": "Mindkit",    "creature_type": "psychic",  "level": 1,
     "moves": ["psychic", "normal"]},
    {"name": "Dreamowl",   "creature_type": "psychic",  "level": 1,
     "moves": ["psychic", "normal"]},
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
    # Ice evolutions
    "Frostpaw": {"level": 5, "evolves_to": "Glacierfang", "stat_bonus": 5,
                 "new_moves": ["ice"]},
    "Glacierfang": {"level": 10, "evolves_to": "Blizzardking", "stat_bonus": 8,
                    "new_moves": ["ice"]},
    "Glacimole": {"level": 5, "evolves_to": "Permafrost", "stat_bonus": 5,
                  "new_moves": ["ice"]},
    # Psychic evolutions
    "Mindkit": {"level": 5, "evolves_to": "Psyblade", "stat_bonus": 5,
                "new_moves": ["psychic"]},
    "Psyblade": {"level": 10, "evolves_to": "Mindlord", "stat_bonus": 8,
                 "new_moves": ["psychic"]},
    "Dreamowl": {"level": 5, "evolves_to": "Nightseer", "stat_bonus": 5,
                 "new_moves": ["psychic"]},
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
    "Glacial Peaks": [
        {"template": 10, "min_level": 1, "max_level": 3},
        {"template": 11, "min_level": 2, "max_level": 4},
    ],
    "Dream Temple": [
        {"template": 12, "min_level": 1, "max_level": 3},
        {"template": 13, "min_level": 2, "max_level": 4},
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
    # -- Ice creatures --
    "Frostpaw": r"""
    /\  /\
   ( o  o ) ❄️
    > ^^ <
   /|    |\
""",
    "Glacimole": r"""
   ___
  (o.o) ❄️
   |_|
  / | \
""",
    "Glacierfang": r"""
      /\  /\
     (❄️  ❄️)~❄️❄️
      > WW <
     /|    |\
    / |    | \
""",
    "Blizzardking": r"""
        👑
       /\  /\  ❄️❄️❄️
      (❄️  ❄️)
       > WW <
     /||    ||\
    / ||    || \
""",
    "Permafrost": r"""
     ___
    (❄.❄) ❄️❄️
    /|_|\
   / | | \
     | |
""",
    # -- Psychic creatures --
    "Mindkit": r"""
    /\  /\
   ( 🔮🔮 )
    > ~~ <
    |    |
""",
    "Dreamowl": r"""
   .-~~~-.
  / 🔮🔮 \
 (  ~~~~  )
  \      /
""",
    "Psyblade": r"""
      /\  /\
     (🔮  🔮)~✨✨
      > ~~ <
     /|    |\
    / |    | \
""",
    "Mindlord": r"""
     ✨  ✨  ✨
       /\  /\
      (🔮  🔮)
       > ~~ <
     //|    |\\
    / /|    |\ \
""",
    "Nightseer": r"""
     .-~===~-.
    / 🔮  🔮  \ ✨
   (  ~~~~~~  )
    \  ~~~~  /
     '-.=.-'
""",
    # -- Dual-type creatures (from breeding) --
    "Steamhound": r"""
    /\  /\
   (🔥💧)~💨
    > ^^ <
   /|    |\
""",
    "Thornflame": r"""
   \|/
  --🔥-- 🌿
   /|\
  / | \
""",
    "Frostwave": r"""
     ><>
   ><(❄°> ❄️💧
     ><>
""",
    "Sparkleaf": r"""
   \|/ ⚡
  --*--
   /|\ 🌿
  / | \
""",
    "Mindshade": r"""
    /\  /\
   (🔮🌙)
    > ~~ <
    |    |
""",
}

# -- Creature abilities --
ABILITIES: dict[str, dict] = {
    "Fireproof":   {"description": "Immune to burn", "blocks_status": "burn"},
    "Waterproof":  {"description": "Immune to poison", "blocks_status": "poison"},
    "Grounded":    {"description": "Immune to stun", "blocks_status": "stun"},
    "Thick Skin":  {"description": "+25% defense", "stat_mod": ("defense", 1.25)},
    "Quick Feet":  {"description": "+25% speed", "stat_mod": ("speed", 1.25)},
    "Power Surge": {"description": "+15% attack", "stat_mod": ("attack", 1.15)},
    "Regenerator": {"description": "Heal 5% HP each turn", "heal_per_turn": 0.05},
    "Intimidate":  {"description": "Opponent -10% attack at battle start", "opponent_mod": ("attack", 0.9)},
}

CREATURE_ABILITIES: dict[str, str] = {
    "Blazepup": "Fireproof", "Cinderax": "Fireproof",
    "Aquafin": "Waterproof", "Tidalynx": "Waterproof",
    "Thornwhip": "Regenerator", "Mossling": "Regenerator",
    "Zappaw": "Quick Feet", "Voltfox": "Quick Feet",
    "Duskfang": "Intimidate", "Gloomwing": "Intimidate",
    "Frostpaw": "Thick Skin", "Glacimole": "Thick Skin",
    "Mindkit": "Power Surge", "Dreamowl": "Grounded",
}

# -- Items --
ITEMS: dict[str, dict] = {
    "Potion":          {"type": "heal", "value": 20,
                        "description": "Restores 20 HP", "price": 10},
    "Super Potion":    {"type": "heal", "value": 50,
                        "description": "Restores 50 HP", "price": 25},
    "Full Heal":       {"type": "full_heal", "value": 0,
                        "description": "Fully restores HP and cures status", "price": 50},
    "Antidote":        {"type": "cure_status", "value": 0,
                        "description": "Cures all status effects", "price": 8},
    "Attack Berry":    {"type": "stat_boost", "stat": "attack", "value": 3,
                        "description": "Permanently +3 ATK", "price": 40},
    "Defense Berry":   {"type": "stat_boost", "stat": "defense", "value": 2,
                        "description": "Permanently +2 DEF", "price": 40},
    "Speed Berry":     {"type": "stat_boost", "stat": "speed", "value": 2,
                        "description": "Permanently +2 SPD", "price": 40},
    "Capture Stone":   {"type": "catch_boost", "value": 0.2,
                        "description": "+20% catch rate", "price": 15},
    "Golden Stone":    {"type": "catch_boost", "value": 0.5,
                        "description": "+50% catch rate", "price": 35},
    "XP Charm":        {"type": "xp_boost", "value": 1.5,
                        "description": "1.5x XP from next battle", "price": 30},
}

# -- Weather conditions --
WEATHER_CONDITIONS: dict[str, dict] = {
    "Sunny":     {"boosts": ["fire"],    "weakens": ["water", "ice"],
                  "description": "\u2600\ufe0f The sun blazes! Fire moves strengthened."},
    "Rainy":     {"boosts": ["water"],   "weakens": ["fire"],
                  "description": "\U0001f327\ufe0f Rain falls! Water moves strengthened."},
    "Windy":     {"boosts": ["nature"],  "weakens": ["fire"],
                  "description": "\U0001f32a\ufe0f Strong winds! Nature moves strengthened."},
    "Stormy":    {"boosts": ["electric"],"weakens": ["water"],
                  "description": "\u26c8\ufe0f Lightning crackles! Electric moves strengthened."},
    "Foggy":     {"boosts": ["shadow", "psychic"], "weakens": ["normal"],
                  "description": "\U0001f32b\ufe0f Dense fog! Shadow & Psychic moves strengthened."},
    "Snowy":     {"boosts": ["ice"],     "weakens": ["nature", "fire"],
                  "description": "\u2744\ufe0f Snow falls! Ice moves strengthened."},
    "Clear":     {"boosts": [],          "weakens": [],
                  "description": "\u2728 Clear skies. No weather effects."},
}

WEATHER_BOOST = 1.3
WEATHER_WEAKEN = 0.7

# -- Achievement definitions --
ACHIEVEMENT_DEFS: list[dict] = [
    {"id": "first_catch",       "name": "Gotta Start Somewhere",  "description": "Catch your first creature",      "icon": "\U0001f3a3"},
    {"id": "catch_10",          "name": "Collector",              "description": "Catch 10 creatures",              "icon": "\U0001f4e6"},
    {"id": "win_first_battle",  "name": "First Victory",         "description": "Win your first battle",           "icon": "\u2694\ufe0f"},
    {"id": "win_10_battles",    "name": "Battle Veteran",         "description": "Win 10 battles",                  "icon": "\U0001f3c5"},
    {"id": "win_50_battles",    "name": "Arena Champion",         "description": "Win 50 battles",                  "icon": "\U0001f3c6"},
    {"id": "first_evolution",   "name": "Growing Up",             "description": "Evolve a creature for the first time", "icon": "\U0001f9ec"},
    {"id": "full_party",        "name": "Squad Goals",            "description": "Fill your party to 6 creatures",  "icon": "\U0001f465"},
    {"id": "level_10",          "name": "Grinder",                "description": "Reach level 10 with a creature",  "icon": "\U0001f4aa"},
    {"id": "all_types",         "name": "Type Master",            "description": "Catch one of every type",         "icon": "\U0001f308"},
    {"id": "no_damage_win",     "name": "Untouchable",            "description": "Win a battle without taking damage", "icon": "\U0001f6e1\ufe0f"},
    {"id": "crit_finish",       "name": "Critical Finisher",      "description": "Win with a critical hit",         "icon": "\U0001f4a5"},
    {"id": "first_breed",       "name": "Creature Breeder",       "description": "Breed your first creature",       "icon": "\U0001f95a"},
    {"id": "tournament_win",    "name": "Tournament Champion",    "description": "Win a tournament",                "icon": "\U0001f451"},
    {"id": "story_complete",    "name": "Hero of the Arena",      "description": "Complete the story mode",         "icon": "\U0001f4d6"},
    {"id": "all_areas",         "name": "World Explorer",         "description": "Visit every exploration area",    "icon": "\U0001f5fa\ufe0f"},
]

# -- Story / quest data --
STORY_CHAPTERS: list[dict] = [
    {
        "id": 1, "title": "The Awakening",
        "intro": "You've just received your first creature! But wild creatures are causing trouble in the Scorched Plains...",
        "area": "Scorched Plains",
        "boss": {"name": "Blazepup", "creature_type": "fire", "level": 4, "moves": ["fire", "normal"]},
        "boss_intro": "\U0001f525 Fire Captain Kai: 'You think you can handle the heat, rookie?'",
        "reward_gold": 50, "reward_item": "Potion",
    },
    {
        "id": 2, "title": "Tidal Troubles",
        "intro": "Strange tides are flooding Crystal Lake. A powerful water creature guards the source...",
        "area": "Crystal Lake",
        "boss": {"name": "Tidalynx", "creature_type": "water", "level": 6, "moves": ["water", "normal"]},
        "boss_intro": "\U0001f4a7 Sailor Marina: 'The lake chose me. You\'ll have to go through me!'",
        "reward_gold": 75, "reward_item": "Super Potion",
    },
    {
        "id": 3, "title": "Thunder Trials",
        "intro": "Lightning has struck Thunder Peak! An electric guardian blocks the pass...",
        "area": "Thunder Peak",
        "boss": {"name": "Voltfox", "creature_type": "electric", "level": 8, "moves": ["electric", "normal"]},
        "boss_intro": "\u26a1 Storm Warden Bolt: 'Feel the power of the storm!'",
        "reward_gold": 100, "reward_item": "Attack Berry",
    },
    {
        "id": 4, "title": "Shadows Unleashed",
        "intro": "Darkness spreads from the Shadow Caverns. Something ancient stirs within...",
        "area": "Shadow Caverns",
        "boss": {"name": "Gloomwing", "creature_type": "shadow", "level": 10, "moves": ["shadow", "normal"]},
        "boss_intro": "\U0001f319 Shadow Keeper Nyx: 'You dare enter my domain?'",
        "reward_gold": 150, "reward_item": "Golden Stone",
    },
    {
        "id": 5, "title": "The Final Challenge",
        "intro": "The Arena Grand Master awaits. Prove you're the ultimate creature trainer!",
        "area": "Mystic Ruins",
        "boss": {"name": "Mindkit", "creature_type": "psychic", "level": 12, "moves": ["psychic", "normal"]},
        "boss_intro": "\U0001f52e Grand Master Sage: 'I\'ve seen your journey. Now show me your true strength!'",
        "reward_gold": 300, "reward_item": "XP Charm",
    },
]

# -- Tournament data --
TOURNAMENT_TIERS: list[dict] = [
    {"name": "Bronze Cup", "level_range": (1, 4), "rounds": 3, "reward_gold": 75},
    {"name": "Silver Cup", "level_range": (3, 7), "rounds": 4, "reward_gold": 150},
    {"name": "Gold Cup",   "level_range": (6, 10), "rounds": 5, "reward_gold": 300},
    {"name": "Champion Cup", "level_range": (9, 14), "rounds": 5, "reward_gold": 500},
]

# -- Breeding compatibility --
BREEDING_TABLE: dict[tuple[str, str], list[str]] = {
    ("fire", "water"):    ["fire", "water"],
    ("fire", "nature"):   ["fire", "nature"],
    ("fire", "ice"):      ["fire", "water"],
    ("water", "nature"):  ["water", "nature"],
    ("water", "ice"):     ["water", "ice"],
    ("electric", "fire"):  ["electric", "fire"],
    ("electric", "water"): ["electric", "water"],
    ("electric", "nature"):["electric", "nature"],
    ("ice", "nature"):    ["ice", "nature"],
    ("psychic", "shadow"):["psychic", "shadow"],
    ("nature", "shadow"): ["nature", "shadow"],
    ("ice", "shadow"):    ["ice", "shadow"],
}

DUAL_TYPE_CREATURES: dict[str, dict] = {
    "Steamhound":   {"primary": "fire",     "secondary": "water",    "ability": "Thick Skin"},
    "Thornflame":   {"primary": "fire",     "secondary": "nature",   "ability": "Fireproof"},
    "Stormpup":     {"primary": "electric", "secondary": "fire",     "ability": "Quick Feet"},
    "Frostwave":    {"primary": "water",    "secondary": "ice",      "ability": "Waterproof"},
    "Sparkleaf":    {"primary": "electric", "secondary": "nature",   "ability": "Regenerator"},
    "Mindshade":    {"primary": "psychic",  "secondary": "shadow",   "ability": "Intimidate"},
    "Glacivine":    {"primary": "ice",      "secondary": "nature",   "ability": "Thick Skin"},
    "Thundertide":  {"primary": "electric", "secondary": "water",    "ability": "Quick Feet"},
}
