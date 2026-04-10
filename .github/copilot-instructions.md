## Project: Creature Collector & Battle Arena
A terminal-based Python game for parents and kids to build together.

## Build & Test
- `python3 -m pytest tests/ -v` for all tests
- `python3 main.py` to play

## Code Style
- Python 3.9+ with `from __future__ import annotations` for modern type hints
- Type hints on all function signatures
- Docstrings on all public methods
- Keep files under 150 lines — small and readable
- Use colorama for colored terminal output

## Architecture
- creature.py: Creature and Move classes, stat calculations
- battle.py: Battle engine, turn loop, damage calculation
- collection.py: Party management (max 6), catching logic
- data.py: Creature definitions, type chart, encounter tables
- display.py: ASCII art, health bars, colored output
- save_manager.py: JSON save/load with schema versioning
- main.py: Game loop, menus, user input handling

## Critical Invariants
- HP must be clamped: 0 <= hp <= max_hp
- Damage must always be >= 1
- Type chart must be symmetric: if A is strong vs B, B resists A
- Save files must include "schema_version" field
- Collection size must never exceed MAX_PARTY_SIZE (6)
- XP gain must be positive
- Level must be >= 1

## Testing Requirements
- Every public method needs at least one test
- Edge cases: zero HP, max level, empty collection, corrupted save
- Battle tests: type advantage, resistance, neutral, critical hit
- Save tests: round-trip, schema migration, special characters
