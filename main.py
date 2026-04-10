"""Creature Collector & Battle Arena — Main game loop."""
from __future__ import annotations

import sys

from creature import Creature
from battle import BattleEngine, calculate_xp_reward
from collection import (
    Collection, create_starter, wild_encounter, catch_attempt, MAX_PARTY_SIZE,
)
from data import STARTER_CREATURES, ENCOUNTER_TABLES, CREATURE_ABILITIES
from display import (
    show_creature, battle_header, battle_message, show_menu, show_moves,
    health_bar, format_status_effects, evolution_message, defend_message,
    animate_attack, animate_evolution, show_weather, show_item,
    show_inventory, show_achievement_unlock, show_tournament_header,
    show_chapter_intro, show_breeding_result, show_trade_code,
    show_creature_name,
)
from save_manager import save_game, load_game, save_full_state, load_full_state

from items import Inventory, get_shop_items
from weather import WeatherSystem
from pokedex import Pokedex
from achievements import AchievementTracker
from tournament import TournamentRunner, get_available_tournaments
from story import StoryProgress
from breeding import can_breed, breed_creatures, get_breeding_preview
from trading import export_creature, import_creature, get_trade_summary
from replay import BattleReplay, ReplayManager


# ---------------------------------------------------------------------------
# GameState — holds all persistent state
# ---------------------------------------------------------------------------

class GameState:
    """Holds all persistent game state."""

    def __init__(
        self,
        collection: Collection,
        inventory: Inventory,
        pokedex: Pokedex,
        achievements: AchievementTracker,
        story: StoryProgress,
        weather: WeatherSystem,
        replay_mgr: ReplayManager,
    ) -> None:
        self.collection = collection
        self.inventory = inventory
        self.pokedex = pokedex
        self.achievements = achievements
        self.story = story
        self.weather = weather
        self.replay_mgr = replay_mgr


def create_new_game_state(collection: Collection) -> GameState:
    """Build a fresh GameState from the given collection."""
    return GameState(
        collection,
        Inventory(),
        Pokedex(),
        AchievementTracker(),
        StoryProgress(),
        WeatherSystem(),
        ReplayManager(),
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


def _get_text_input(prompt: str) -> str:
    """Get free-text input from the player."""
    return input(prompt).strip()


def _display_new_achievements(state: GameState) -> None:
    """Check and display any newly unlocked achievements."""
    newly = state.achievements.check_achievements()
    for ach in newly:
        print(show_achievement_unlock(ach))


# ---------------------------------------------------------------------------
# choose_starter — assigns ability
# ---------------------------------------------------------------------------

def choose_starter() -> Collection:
    """Let the player pick their first creature."""
    print("\n🥚 Choose your starter creature!\n")
    for i, template in enumerate(STARTER_CREATURES):
        print(f"  {i + 1}. {template['name']} ({template['creature_type']})")
    choice = get_input("\nYour choice: ", range(1, len(STARTER_CREATURES) + 1))
    if choice == -1:
        sys.exit(0)
    starter = create_starter(choice - 1)
    starter.ability = CREATURE_ABILITIES.get(starter.name)
    print(f"\n🎉 You chose {starter.name}!")
    print(show_creature(starter))
    return Collection(creatures=[starter])


# ---------------------------------------------------------------------------
# Battle display helper
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# run_battle — with weather, replay, animations
# ---------------------------------------------------------------------------

def run_battle(state: GameState, opponent: Creature) -> bool:
    """Run a turn-based battle. Returns True if the player won."""
    collection = state.collection
    player = collection.get_active()
    if player is None:
        print("  You have no creatures to battle with!")
        return False

    engine = BattleEngine(player, opponent)
    replay = BattleReplay(player.name, opponent.name)

    # Show weather at battle start
    print(show_weather(state.weather.current, state.weather.get_description()))
    print(battle_header(player, opponent))

    player_hp_start = player.hp

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
            for eff, dmg in status_results:
                if dmg > 0:
                    print(battle_message(
                        f"  {creature.name} took {dmg} from {eff}!",
                        "not_effective",
                    ))
                    replay.record_status(creature.name, eff, dmg)

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
                    return False

                if move_choice == num_moves + 1:
                    engine.player_defend()
                    print(defend_message(player.name))
                    replay.record_defend(player.name)
                else:
                    move = player.moves[move_choice - 1]
                    damage, mult, crit, effect = engine.player_turn(move)
                    animate_attack(move.move_type)
                    _display_attack(
                        player.name, move.name, damage, mult, crit,
                        effect, opponent.name,
                    )
                    replay.record_attack(
                        player.name, move.name, damage, crit, mult, effect,
                    )
            else:
                # Opponent turn
                opp_move, opp_dmg, opp_mult, opp_crit, opp_effect = (
                    engine.opponent_turn()
                )
                if opp_move is None:
                    print(defend_message(opponent.name))
                    replay.record_defend(opponent.name)
                else:
                    animate_attack(opp_move.move_type)
                    _display_attack(
                        opponent.name, opp_move.name, opp_dmg, opp_mult,
                        opp_crit, opp_effect, player.name,
                    )
                    replay.record_attack(
                        opponent.name, opp_move.name, opp_dmg, opp_crit,
                        opp_mult, opp_effect,
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
        return False

    won = result.winner is player

    if won:
        replay.set_result(player.name)
        print(battle_message(f"\n🏆 {player.name} wins!", "level_up"))
        xp = calculate_xp_reward(opponent)
        old_name = player.name
        leveled, evolved_name = player.gain_xp(xp)
        print(f"  +{xp} XP!")

        # Achievement tracking
        state.achievements.increment_stat("battles_won")
        if player.hp >= player_hp_start:
            state.achievements.increment_stat("no_damage_wins")
        if player.level >= 10:
            state.achievements.increment_stat("max_level", player.level)

        if evolved_name:
            animate_evolution(old_name, evolved_name)
            print(evolution_message(old_name, evolved_name))
            print(show_creature(player))
            state.achievements.increment_stat("evolutions")
            replay.record_event("evolution", {
                "creature": old_name, "new_form": evolved_name,
            })
        elif leveled:
            print(battle_message(
                f"  🎉 {player.name} leveled up to Lv.{player.level}!",
                "level_up",
            ))
            replay.record_event("level_up", {
                "creature": player.name, "level": player.level,
            })
    else:
        replay.set_result(opponent.name)
        print(battle_message(f"\n💀 {player.name} fainted...", "faint"))
        player.heal()
        print(f"  {player.name} was healed back to full HP.")

    # Save replay
    state.replay_mgr.save_replay(replay)

    _display_new_achievements(state)
    return won


# ---------------------------------------------------------------------------
# Explore — weather, pokedex, achievements
# ---------------------------------------------------------------------------

def explore(state: GameState) -> None:
    """Explore an area and encounter a wild creature."""
    # Tick weather
    new_weather = state.weather.tick()
    if new_weather:
        print(show_weather(new_weather, state.weather.get_description()))

    areas = list(ENCOUNTER_TABLES.keys())
    print(show_menu("🗺️  Choose an area to explore:", areas))
    choice = get_input("\nYour choice: ", range(1, len(areas) + 1))
    if choice == -1:
        return
    area = areas[choice - 1]

    # Show current weather
    print(show_weather(state.weather.current, state.weather.get_description()))

    # Mark area visited
    state.pokedex.mark_area(area)
    state.achievements.increment_stat(
        "areas_visited", len(state.pokedex.areas_visited),
    )
    # Overwrite with actual count (not cumulative increment)
    state.achievements.stats["areas_visited"] = len(state.pokedex.areas_visited)

    wild = wild_encounter(area)
    if wild is None:
        print("  Nothing appeared...")
        _display_new_achievements(state)
        return
    print(f"\n🌿 A wild {wild.name} (Lv.{wild.level}) appeared!")
    print(show_creature(wild))

    # Pokedex: mark as seen
    state.pokedex.mark_seen(wild.name)

    options = ["Battle!", "Run away"]
    print(show_menu("What do you want to do?", options))
    action = get_input("Your choice: ", range(1, 3))
    if action == 1:
        won = run_battle(state, wild)
        if won:
            # Offer to catch
            if not state.collection.is_full():
                print(show_menu("Try to catch it?", ["Yes!", "No"]))
                catch_choice = get_input("Your choice: ", range(1, 3))
                if catch_choice == 1:
                    if catch_attempt(wild):
                        wild.heal()
                        state.collection.add_creature(wild)
                        print(battle_message(
                            f"  ✨ You caught {wild.name}!", "catch",
                        ))
                        state.pokedex.mark_caught(wild.name)
                        state.achievements.increment_stat("creatures_caught")
                        # Track types caught
                        types_caught = {c.creature_type for c in state.collection.creatures}
                        state.achievements.stats["types_caught"] = len(types_caught)
                        # Track max party size
                        state.achievements.stats["max_party_size"] = len(
                            state.collection.creatures
                        )
                    else:
                        print(f"  {wild.name} broke free!")
    else:
        print("  You ran away safely!")

    _display_new_achievements(state)


# ---------------------------------------------------------------------------
# Manage Party — with nickname support
# ---------------------------------------------------------------------------

def manage_party(state: GameState) -> None:
    """View and manage the creature party."""
    collection = state.collection
    if not collection.creatures:
        print("  Your party is empty!")
        return
    print(f"\n📦 Your Party ({len(collection.creatures)}/{MAX_PARTY_SIZE}):\n")
    for i, creature in enumerate(collection.creatures):
        active = " ⭐" if i == collection.active_index else ""
        name = show_creature_name(creature)
        print(f"  {i + 1}. {name} (Lv.{creature.level}) "
              f"HP: {creature.hp}/{creature.max_hp}{active}")

    options = [
        "View details", "Swap active creature", "Heal all",
        "Nickname a creature", "Back",
    ]
    print(show_menu("Party options:", options))
    choice = get_input("Your choice: ", range(1, len(options) + 1))

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
    elif choice == 4:
        idx = get_input("Which creature? ", range(1, len(collection.creatures) + 1))
        if idx > 0:
            nick = _get_text_input("  Enter nickname (blank to clear): ")
            creature = collection.creatures[idx - 1]
            creature.nickname = nick if nick else None
            if nick:
                print(f"  {creature.name} is now known as \"{nick}\"!")
            else:
                print(f"  Nickname cleared for {creature.name}.")


# ---------------------------------------------------------------------------
# Shop
# ---------------------------------------------------------------------------

def shop(state: GameState) -> None:
    """Buy items from the shop."""
    print(show_inventory(state.inventory.items, state.inventory.gold))
    items = get_shop_items()
    if not items:
        print("  Shop is empty!")
        return
    names: list[str] = []
    for name, data in items:
        names.append(name)
        print(show_item(name, data, state.inventory.get_quantity(name)))
    names.append("Back")
    idx = get_input("\nBuy which item? (or last to go back): ", range(1, len(names) + 1))
    if idx == -1 or idx == len(names):
        return
    item_name = names[idx - 1]
    if state.inventory.buy_item(item_name):
        print(f"  ✅ Bought {item_name}! (💰 {state.inventory.gold}g remaining)")
    else:
        print("  ❌ Not enough gold!")


# ---------------------------------------------------------------------------
# Use Item
# ---------------------------------------------------------------------------

def use_item(state: GameState) -> None:
    """Use an item on a creature."""
    if not state.inventory.items:
        print("  Your inventory is empty!")
        return
    print(show_inventory(state.inventory.items, state.inventory.gold))
    item_names = list(state.inventory.items.keys())
    print(show_menu("Pick an item to use:", item_names + ["Back"]))
    idx = get_input("Your choice: ", range(1, len(item_names) + 2))
    if idx == -1 or idx == len(item_names) + 1:
        return
    item_name = item_names[idx - 1]

    collection = state.collection
    if not collection.creatures:
        print("  No creatures in party!")
        return
    print(show_menu("Use on which creature?", [
        f"{c.name} (Lv.{c.level} HP:{c.hp}/{c.max_hp})"
        for c in collection.creatures
    ]))
    cidx = get_input("Your choice: ", range(1, len(collection.creatures) + 1))
    if cidx == -1:
        return
    success, msg = state.inventory.use_item(item_name, collection.creatures[cidx - 1])
    print(f"  {'✅' if success else '❌'} {msg}")


# ---------------------------------------------------------------------------
# Tournament
# ---------------------------------------------------------------------------

def run_tournament(state: GameState) -> None:
    """Enter a battle tournament."""
    active = state.collection.get_active()
    if active is None:
        print("  You need a creature to enter a tournament!")
        return
    tiers = get_available_tournaments(active.level)
    if not tiers:
        print("  No tournaments available for your level. Train more!")
        return
    tier_names = [f"{t['name']} (Lv.{t['level_range'][0]}-{t['level_range'][1]}, "
                  f"{t['rounds']} rounds, 💰{t['reward_gold']}g)" for t in tiers]
    print(show_menu("🏟️ Available Tournaments:", tier_names + ["Back"]))
    idx = get_input("Your choice: ", range(1, len(tiers) + 2))
    if idx == -1 or idx == len(tiers) + 1:
        return
    tier = tiers[idx - 1]
    runner = TournamentRunner(tier)

    while True:
        opp = runner.get_current_opponent()
        if opp is None:
            break
        display_round = runner.current_round + 1
        print(show_tournament_header(tier["name"], display_round, tier["rounds"]))
        print(f"\n  Opponent: {opp.name} (Lv.{opp.level})")

        won = run_battle(state, opp)
        if won:
            runner.record_win()
            if not runner.advance():
                break  # tournament done
            state.collection.get_active().heal()  # type: ignore[union-attr]
        else:
            runner.record_loss()
            print("  💀 Tournament over — you lost a round.")
            break

    gold = runner.get_reward_gold()
    state.inventory.gold += gold
    print(f"\n  💰 Tournament reward: {gold}g!")
    if runner.is_victory():
        print(battle_message("  🏆 Perfect tournament victory!", "level_up"))
        state.achievements.increment_stat("tournaments_won")
    _display_new_achievements(state)


# ---------------------------------------------------------------------------
# Story Mode
# ---------------------------------------------------------------------------

def story_mode(state: GameState) -> None:
    """Play through story chapters."""
    if not state.story.is_chapter_available():
        print("  📖 Story complete! You've finished all chapters.")
        return
    chapter = state.story.get_current_chapter()
    if chapter is None:
        print("  📖 Story complete!")
        return
    print(show_chapter_intro(chapter))

    print(show_menu("Ready to face the boss?", ["Let's go!", "Not yet"]))
    ready = get_input("Your choice: ", range(1, 3))
    if ready != 1:
        return

    boss = state.story.create_boss()
    print(f"\n  🔥 Boss: {boss.name} (Lv.{boss.level})")

    won = run_battle(state, boss)
    if won:
        completed = state.story.complete_chapter()
        gold = completed.get("reward_gold", 0)
        reward_item = completed.get("reward_item")
        state.inventory.gold += gold
        print(f"\n  📖 Chapter {completed['id']} complete!")
        print(f"  💰 +{gold}g")
        if reward_item:
            state.inventory.add_item(reward_item)
            print(f"  🎁 Received {reward_item}!")
        state.achievements.stats["chapters_complete"] = len(
            state.story.completed_chapters
        )
        _display_new_achievements(state)
    else:
        print("  Try again when you're stronger!")


# ---------------------------------------------------------------------------
# Breeding
# ---------------------------------------------------------------------------

def breed_menu(state: GameState) -> None:
    """Breed two creatures to produce an offspring."""
    creatures = state.collection.creatures
    if len(creatures) < 2:
        print("  You need at least 2 creatures to breed!")
        return
    names = [f"{c.name} (Lv.{c.level}, {c.creature_type})" for c in creatures]
    print(show_menu("Pick first parent:", names))
    idx_a = get_input("Your choice: ", range(1, len(creatures) + 1))
    if idx_a == -1:
        return
    print(show_menu("Pick second parent:", names))
    idx_b = get_input("Your choice: ", range(1, len(creatures) + 1))
    if idx_b == -1:
        return
    if idx_a == idx_b:
        print("  Can't breed a creature with itself!")
        return
    parent_a = creatures[idx_a - 1]
    parent_b = creatures[idx_b - 1]
    if not can_breed(parent_a, parent_b):
        print("  These creatures can't breed! (Need Lv.5+, compatible types, both healthy)")
        return

    print(f"\n{get_breeding_preview(parent_a, parent_b)}")
    print(show_menu("Proceed with breeding?", ["Yes!", "No"]))
    confirm = get_input("Your choice: ", range(1, 3))
    if confirm != 1:
        return

    offspring = breed_creatures(parent_a, parent_b)
    if offspring is None:
        print("  Breeding failed!")
        return
    print(show_breeding_result(offspring))
    if state.collection.is_full():
        print("  ⚠️ Party is full! Offspring was not added.")
    else:
        state.collection.add_creature(offspring)
        print(f"  ✅ {offspring.name} added to your party!")
        state.pokedex.mark_caught(offspring.name)
    state.achievements.increment_stat("breeds")
    _display_new_achievements(state)


# ---------------------------------------------------------------------------
# Pokédex
# ---------------------------------------------------------------------------

def show_pokedex(state: GameState) -> None:
    """Display Pokédex summary."""
    print(f"\n{state.pokedex.get_summary()}")
    if state.pokedex.seen:
        print("\n  Seen:")
        for name in sorted(state.pokedex.seen):
            caught = "✅" if name in state.pokedex.caught else "👁️"
            print(f"    {caught} {name}")
    if state.pokedex.areas_visited:
        print(f"\n  Areas visited: {', '.join(sorted(state.pokedex.areas_visited))}")


# ---------------------------------------------------------------------------
# Achievements
# ---------------------------------------------------------------------------

def show_achievements(state: GameState) -> None:
    """Display achievement progress."""
    from data import ACHIEVEMENT_DEFS
    print(f"\n{state.achievements.get_progress_summary()}\n")
    for ach in ACHIEVEMENT_DEFS:
        unlocked = state.achievements.is_unlocked(ach["id"])
        icon = "✅" if unlocked else "🔒"
        print(f"  {icon} {ach.get('icon', '🏆')} {ach['name']} — {ach['description']}")


# ---------------------------------------------------------------------------
# Trading
# ---------------------------------------------------------------------------

def trade_menu(state: GameState) -> None:
    """Export or import creatures via trade codes."""
    print(show_menu("📤 Trading:", ["Export a creature", "Import a creature", "Back"]))
    choice = get_input("Your choice: ", range(1, 4))
    if choice == 1:
        creatures = state.collection.creatures
        if len(creatures) <= 1:
            print("  You need more than one creature to trade one away!")
            return
        names = [f"{c.name} (Lv.{c.level})" for c in creatures]
        print(show_menu("Export which creature?", names))
        idx = get_input("Your choice: ", range(1, len(creatures) + 1))
        if idx == -1:
            return
        creature = creatures[idx - 1]
        code = export_creature(creature)
        print(show_trade_code(code))
    elif choice == 2:
        code = _get_text_input("  Paste trade code: ")
        if not code:
            return
        summary = get_trade_summary(code)
        if summary is None:
            print("  ❌ Invalid trade code!")
            return
        print(f"\n  {summary}")
        print(show_menu("Import this creature?", ["Yes!", "No"]))
        confirm = get_input("Your choice: ", range(1, 3))
        if confirm != 1:
            return
        imported = import_creature(code)
        if imported is None:
            print("  ❌ Import failed!")
            return
        if state.collection.is_full():
            print("  ⚠️ Party is full!")
        else:
            state.collection.add_creature(imported)
            state.pokedex.mark_caught(imported.name)
            print(f"  ✅ {imported.name} added to your party!")


# ---------------------------------------------------------------------------
# Battle Replays
# ---------------------------------------------------------------------------

def view_replays(state: GameState) -> None:
    """Browse and replay saved battles."""
    replays = state.replay_mgr.load_replays()
    if not replays:
        print("  No replays saved yet!")
        return
    summaries = state.replay_mgr.get_replay_list()
    print(show_menu("⏪ Battle Replays:", summaries + ["Back"]))
    idx = get_input("Your choice: ", range(1, len(summaries) + 2))
    if idx == -1 or idx == len(summaries) + 1:
        return
    replay = replays[idx - 1]
    print(f"\n  📽️ Replaying: {replay.get_summary()}\n")
    for line in ReplayManager.playback(replay):
        print(f"  {line}")


# ---------------------------------------------------------------------------
# Save helpers
# ---------------------------------------------------------------------------

def _save_game(state: GameState) -> bool:
    """Save full game state."""
    return save_full_state(
        state.collection,
        inventory=state.inventory,
        pokedex=state.pokedex,
        achievements=state.achievements,
        story=state.story,
    )


def _load_game_state() -> GameState | None:
    """Load full game state from disk."""
    raw = load_full_state()
    if raw is None:
        return None
    collection = raw.get("collection")
    if collection is None:
        return None
    gs = create_new_game_state(collection)
    if "inventory" in raw:
        gs.inventory = raw["inventory"]
    if "pokedex" in raw:
        gs.pokedex = raw["pokedex"]
    if "achievements" in raw:
        gs.achievements = raw["achievements"]
    if "story" in raw:
        gs.story = raw["story"]
    return gs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Main game loop."""
    print("\n" + "=" * 50)
    print("  🏟️  CREATURE COLLECTOR & BATTLE ARENA  🏟️")
    print("=" * 50)

    options = ["New Game", "Continue", "Quit"]
    print(show_menu("Main Menu:", options))
    choice = get_input("Your choice: ", range(1, 4))

    state: GameState | None = None

    if choice == 2:
        state = _load_game_state()
        if state:
            print(f"  ✅ Loaded save with {len(state.collection.creatures)} creatures!")
        else:
            print("  No save file found. Starting new game...")
    if choice == 3 or choice == -1:
        print("  Goodbye! 👋")
        return
    if state is None:
        collection = choose_starter()
        state = create_new_game_state(collection)
        # Mark starter in pokedex
        starter = collection.get_active()
        if starter:
            state.pokedex.mark_caught(starter.name)

    # Game loop
    while True:
        options = [
            "Explore (find wild creatures)",   # 1
            "Manage Party",                    # 2
            "Shop (buy items)",                # 3
            "Use Item",                        # 4
            "Tournament",                      # 5
            "Story Mode",                      # 6
            "Breeding",                        # 7
            "Pokédex",                         # 8
            "Achievements",                    # 9
            "Trading",                         # 10
            "Battle Replays",                  # 11
            "Save Game",                       # 12
            "Quit",                            # 13
        ]
        print(show_menu("\n🎮 What would you like to do?", options))
        action = get_input("Your choice: ", range(1, len(options) + 1))

        if action == 1:
            explore(state)
        elif action == 2:
            manage_party(state)
        elif action == 3:
            shop(state)
        elif action == 4:
            use_item(state)
        elif action == 5:
            run_tournament(state)
        elif action == 6:
            story_mode(state)
        elif action == 7:
            breed_menu(state)
        elif action == 8:
            show_pokedex(state)
        elif action == 9:
            show_achievements(state)
        elif action == 10:
            trade_menu(state)
        elif action == 11:
            view_replays(state)
        elif action == 12:
            if _save_game(state):
                print("  💾 Game saved!")
            else:
                print("  ❌ Could not save game.")
        elif action in (13, -1):
            print(show_menu("Save before quitting?", ["Yes", "No"]))
            save_choice = get_input("Your choice: ", range(1, 3))
            if save_choice == 1:
                _save_game(state)
                print("  💾 Game saved!")
            print("  Goodbye! 👋")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Interrupted! Goodbye! 👋")
        sys.exit(0)
