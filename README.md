# 🏟️ Creature Collector & Battle Arena

A terminal-based creature battling game built by parents and kids together, using GitHub Copilot CLI's experimental Rubber Duck feature.

## Quick Start

```bash
pip install -r requirements.txt
python3 main.py
```

## How to Play

1. **Start a new game** or load your saved collection
2. **Explore** different areas to find wild creatures
3. **Battle** wild creatures with status effects, weather, and abilities
4. **Catch** weakened creatures to add to your party (max 6)
5. **Level up** and watch creatures evolve automatically
6. **Shop** for potions, berries, and capture stones
7. **Enter tournaments** for multi-round gauntlet battles
8. **Play story mode** through 5 chapters with boss battles
9. **Breed** creatures to create dual-type offspring
10. **Trade** creatures with friends via shareable codes
11. **Save** your progress at any time

## Features

### 🎮 13 Game Systems
| Feature | Description |
|---|---|
| ⚔️ **Battle Engine** | Turn-based with speed priority, defend action, critical hits |
| 🌿 **7 Types** | Fire, Water, Nature, Electric, Shadow, Ice, Psychic |
| 🧬 **Evolution** | 21 evolution chains, auto-evolves at level thresholds |
| ☠️ **Status Effects** | Poison, Burn, Stun, Shield, Boost with duration tracking |
| 🌤️ **Weather** | Dynamic weather boosts/weakens move types each battle |
| 💡 **Abilities** | 8 passive abilities (Fireproof, Regenerator, Intimidate...) |
| 🎒 **Items & Shop** | Potions, stat berries, capture stones, XP charms |
| 🏟️ **Tournaments** | Bronze → Silver → Gold → Champion cup gauntlets |
| 📖 **Story Mode** | 5 chapters with bosses, dialogue, and rewards |
| 🥚 **Breeding** | Combine creatures for dual-type offspring |
| 📤 **Trading** | Export/import creatures as shareable codes |
| 🏆 **Achievements** | 15 badges to unlock (Collector, Untouchable, Type Master...) |
| 📖 **Pokédex** | Track creatures seen and caught |

### 🔥 Type Chart
```
🔥 Fire    → beats 🌿 Nature, ❄️ Ice
💧 Water   → beats 🔥 Fire
🌿 Nature  → beats 💧 Water, ⚡ Electric
⚡ Electric → beats 💧 Water
🌙 Shadow  → beats ⚡ Electric, 🔮 Psychic
❄️ Ice     → beats 🌿 Nature, 🌙 Shadow
🔮 Psychic → beats 🌙 Shadow
```

## Running Tests

```bash
python3 -m pytest tests/ -v
```

## Project Structure

```
creature-arena/
├── main.py           # Game loop and 13 menu options
├── creature.py       # Creature & Move classes (nickname, ability, dual-type)
├── battle.py         # Battle engine (weather, abilities, status effects)
├── collection.py     # Party management & catching
├── data.py           # 14 starters, 24 moves, 21 evolutions, type chart
├── display.py        # ASCII art, animations, colored output
├── evolution.py      # Autonomous evolution system
├── items.py          # Item definitions & inventory
├── weather.py        # Dynamic weather system
├── pokedex.py        # Creature journal
├── achievements.py   # Badge/milestone tracker
├── tournament.py     # Tournament gauntlet mode
├── story.py          # Story/quest progression
├── breeding.py       # Creature breeding system
├── trading.py        # Shareable creature codes
├── replay.py         # Battle recording & playback
├── save_manager.py   # JSON save/load with schema versioning
└── tests/            # Comprehensive test suite
```

## Built With

- Python 3.9+
- [GitHub Copilot CLI](https://github.com/features/copilot/cli) with Rubber Duck 🦆
