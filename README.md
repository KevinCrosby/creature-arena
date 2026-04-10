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
3. **Battle** wild creatures in turn-based combat
4. **Catch** weakened creatures to add to your party (max 6)
5. **Level up** your creatures by winning battles
6. **Save** your progress at any time

## Creature Types

```
🔥 Fire  → strong vs 🌿 Nature → strong vs 💧 Water → strong vs 🔥 Fire
⚡ Electric → strong vs 💧 Water
🌙 Shadow → strong vs ⚡ Electric
```

## Running Tests

```bash
python3 -m pytest tests/ -v
```

## Project Structure

```
creature-arena/
├── main.py           # Game loop and menus
├── creature.py       # Creature & Move classes
├── battle.py         # Turn-based battle engine
├── collection.py     # Party management & catching
├── data.py           # Creature definitions & type chart
├── display.py        # ASCII art & colored output
├── save_manager.py   # JSON save/load
└── tests/            # Test suite
```

## Built With

- Python 3.9+
- [GitHub Copilot CLI](https://github.com/features/copilot/cli) with Rubber Duck 🦆
