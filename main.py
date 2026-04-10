"""Creature Collector & Battle Arena — Main game loop."""
from __future__ import annotations

import sys

from creature import Creature
from battle import BattleEngine, calculate_xp_reward
from collection import (
    Collection, create_starter, wild_encounter, catch_attempt, MAX_PARTY_SIZE,
)
from data import STARTER_CREATURES, ENCOUNTER_TABLES
from display import (
    show_creature, battle_header, battle_message, show_menu, show_moves,
    health_bar, format_status_effects, evolution_message, defend_message,
)
from save_manager import save_game, load_game


def get_input(prompt: str, valid_range: range) -> int:
    """Get a validated numeric input from the player."""
    while True:
        try:
            raw = input(prompt).strip()
            if raw.lower() in ("q", "quit"):
                return -1
            choice = int(raw)
            if choice in valid_range:
                return choice
            print(f"  Please enter a number between {valid_range.start} and {valid_range.stop - 1}.")
        except ValueError:
            print("  Please enter a number.")


def choose_starter() -> Collection:
    """Let the player pick their first creature."""
    print("\n🥚 Choose your starter creature!\n")
    for i, template in enumerate(STARTER_CREATURES):
        print(f"  {i + 1}. {template['name']} ({template['creature_type']})")
    choice = get_input("\nYour choice: ", range(1, len(STARTER_CREATURES) + 1))
    if choice == -1:
        sys.exit(0)
    starter = create_starter(choice - 1)
    print(f"\n🎉 You chose {starter.name}!")
    print(show_creature(starter))
    return Collection(creatures=[starter])


def explore(collection: Collection) -> None:
    """Explore an area and encounter a wild creature."""
    areas = list(ENCOUNTER_TABLES.keys())
    print(show_menu("🗺️  Choose an area to explore:", areas))
    choice = get_input("\nYour choice: ", range(1, len(areas) + 1))
    if choice == -1:
        return
    area = areas[choice - 1]
    wild = wild_encounter(area)
    if wild is None:
        print("  Nothing appeared...")
        return
    print(f"\n🌿 A wild {wild.name} (Lv.{wild.level}) appeared!")
    print(show_creature(wild))

    options = ["Battle!", "Run away"]
    print(show_menu("What do you want to do?", options))
    action = get_input("Your choice: ", range(1, 3))
    if action == 1:
        run_battle(collection, wild)
    else:
        print("  You ran away safely!")


def _display_attack(attacker_name: str, move_name: str, damage: int,
                    mult: float, crit: bool, effect: str | None,
                    target_name: str) -> None:
    """Display attack results including effectiveness, crits, and effects."""
    msg = f"  {attacker_name} used {move_name}! ({damage} damage)"
    if mult > 1.0:
        print(battle_message(msg + " Super effective!", "super_effective"))
    elif mult < 1.0:
        print(battle_message(msg + " Not very effective...", "not_effective"))
    else:
        print(f"  {msg}")
    if crit:
        print(battle_message("  💥 Critical hit!", "critical"))
    if effect:
        print(battle_message(f"  {target_name} was {effect}ed!", "info"))


def run_battle(collection: Collection, opponent: Creature) -> None:
    """Run a turn-based battle with status effects, speed-based turns, and defend."""
    player = collection.get_active()
    if player is None:
        print("  You have no creatures to battle with!")
        return

    engine = BattleEngine(player, opponent)
    print(battle_header(player, opponent))

    while not engine.is_battle_over():
        engine.turn_count += 1
        print(f"\n--- Turn {engine.turn_count} ---")

        turn_order = engine.get_turn_order()

        for actor in turn_order:
            if engine.is_battle_over():
                break

            creature = player if actor == "player" else opponent

            # Process status effects at start of turn
            status_results = engine.process_turn_start(creature)
            for effect, damage in status_results:
                if damage > 0:
                    print(battle_message(
                        f"  {creature.name} took {damage} from {effect}!",
                        "not_effective",
                    ))

            if engine.is_battle_over():
                break

            if creature.is_stunned():
                print(battle_message(
                    f"  ⚡ {creature.name} is stunned and can't move!",
                    "not_effective",
                ))
                continue

            if actor == "player":
                # Show moves + defend option
                print(f"\n{player.name}'s moves:")
                print(show_moves(player))
                num_moves = len(player.moves)
                print(f"  {num_moves + 1}. 🛡️ Defend")

                move_choice = get_input(
                    "Pick a move: ", range(1, num_moves + 2),
                )
                if move_choice == -1:
                    print("  You fled the battle!")
                    player.heal()
                    return

                if move_choice == num_moves + 1:
                    engine.player_defend()
                    print(defend_message(player.name))
                else:
                    move = player.moves[move_choice - 1]
                    damage, mult, crit, effect = engine.player_turn(move)
                    _display_attack(
                        player.name, move.name, damage, mult, crit,
                        effect, opponent.name,
                    )
            else:
                # Opponent turn
                opp_move, opp_dmg, opp_mult, opp_crit, opp_effect = (
                    engine.opponent_turn()
                )
                if opp_move is None:
                    print(defend_message(opponent.name))
                else:
                    _display_attack(
                        opponent.name, opp_move.name, opp_dmg, opp_mult,
                        opp_crit, opp_effect, player.name,
                    )

        # Show HP and status effects after both turns
        print(f"\n  {player.name}: {health_bar(player.hp, player.max_hp)}")
        print(f"  {opponent.name}: {health_bar(opponent.hp, opponent.max_hp)}")
        for c in [player, opponent]:
            effects = format_status_effects(c)
            if effects:
                print(f"  {c.name}: {effects}")

    # Battle result
    result = engine.get_result()
    if result is None:
        return

    if result.winner is player:
        print(battle_message(f"\n🏆 {player.name} wins!", "level_up"))
        xp = calculate_xp_reward(opponent)
        old_name = player.name
        leveled, evolved_name = player.gain_xp(xp)
        print(f"  +{xp} XP!")
        if evolved_name:
            print(evolution_message(old_name, evolved_name))
            print(show_creature(player))
        elif leveled:
            print(battle_message(
                f"  🎉 {player.name} leveled up to Lv.{player.level}!",
                "level_up",
            ))
        # Offer to catch
        if not collection.is_full():
            print(show_menu("Try to catch it?", ["Yes!", "No"]))
            catch_choice = get_input("Your choice: ", range(1, 3))
            if catch_choice == 1:
                if catch_attempt(opponent):
                    opponent.heal()
                    collection.add_creature(opponent)
                    print(battle_message(
                        f"  ✨ You caught {opponent.name}!", "catch",
                    ))
                else:
                    print(f"  {opponent.name} broke free!")
    else:
        print(battle_message(f"\n💀 {player.name} fainted...", "faint"))
        player.heal()
        print(f"  {player.name} was healed back to full HP.")


def manage_party(collection: Collection) -> None:
    """View and manage the creature party."""
    if not collection.creatures:
        print("  Your party is empty!")
        return
    print(f"\n📦 Your Party ({len(collection.creatures)}/{MAX_PARTY_SIZE}):\n")
    for i, creature in enumerate(collection.creatures):
        active = " ⭐" if i == collection.active_index else ""
        print(f"  {i + 1}. {creature.name} (Lv.{creature.level}) "
              f"HP: {creature.hp}/{creature.max_hp}{active}")

    options = ["View details", "Swap active creature", "Heal all", "Back"]
    print(show_menu("Party options:", options))
    choice = get_input("Your choice: ", range(1, 5))

    if choice == 1:
        idx = get_input("Which creature? ", range(1, len(collection.creatures) + 1))
        if idx > 0:
            print(f"\n{show_creature(collection.creatures[idx - 1])}")
    elif choice == 2:
        idx = get_input("Set active: ", range(1, len(collection.creatures) + 1))
        if idx > 0 and collection.swap_active(idx - 1):
            print(f"  ⭐ {collection.creatures[idx - 1].name} is now active!")
    elif choice == 3:
        collection.heal_all()
        print("  💚 All creatures healed!")


def main() -> None:
    """Main game loop."""
    print("\n" + "=" * 50)
    print("  🏟️  CREATURE COLLECTOR & BATTLE ARENA  🏟️")
    print("=" * 50)

    options = ["New Game", "Continue", "Quit"]
    print(show_menu("Main Menu:", options))
    choice = get_input("Your choice: ", range(1, 4))

    collection: Collection | None = None

    if choice == 2:
        collection = load_game()
        if collection:
            print(f"  ✅ Loaded save with {len(collection.creatures)} creatures!")
        else:
            print("  No save file found. Starting new game...")
    if choice == 3 or choice == -1:
        print("  Goodbye! 👋")
        return
    if collection is None:
        collection = choose_starter()

    # Game loop
    while True:
        options = ["Explore (find wild creatures)", "Manage Party", "Save Game", "Quit"]
        print(show_menu("\n🎮 What would you like to do?", options))
        action = get_input("Your choice: ", range(1, 5))

        if action == 1:
            explore(collection)
        elif action == 2:
            manage_party(collection)
        elif action == 3:
            if save_game(collection):
                print("  💾 Game saved!")
            else:
                print("  ❌ Could not save game.")
        elif action in (4, -1):
            print(show_menu("Save before quitting?", ["Yes", "No"]))
            save_choice = get_input("Your choice: ", range(1, 3))
            if save_choice == 1:
                save_game(collection)
                print("  💾 Game saved!")
            print("  Goodbye! 👋")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Interrupted! Goodbye! 👋")
        sys.exit(0)
