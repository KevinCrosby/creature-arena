"""Display utilities: health bars, ASCII art, colored terminal output, animations."""
from __future__ import annotations

import sys
import time

from colorama import Fore, Style, init as colorama_init

from creature import Creature
from data import CREATURE_ART, ABILITIES

# Initialize colorama for cross-platform color support
colorama_init(autoreset=True)

TYPE_COLORS: dict[str, str] = {
    "fire": Fore.RED,
    "water": Fore.BLUE,
    "nature": Fore.GREEN,
    "electric": Fore.YELLOW,
    "shadow": Fore.MAGENTA,
    "normal": Fore.WHITE,
    "ice": Fore.CYAN,
    "psychic": Fore.MAGENTA + Style.BRIGHT,
}

TYPE_EMOJI: dict[str, str] = {
    "fire": "🔥",
    "water": "💧",
    "nature": "🌿",
    "electric": "⚡",
    "shadow": "🌙",
    "normal": "⭐",
    "ice": "❄️",
    "psychic": "🔮",
}

STATUS_ICONS: dict[str, str] = {
    "poison": "☠️",
    "burn": "🔥",
    "stun": "⚡",
    "shield": "🛡️",
    "boost": "💪",
}

BAR_LENGTH = 20


def format_status_effects(creature: Creature) -> str:
    """Format active status effects as a string with icons."""
    if not creature.status_effects:
        return ""
    parts = []
    for effect, turns in creature.status_effects.items():
        icon = STATUS_ICONS.get(effect, "❓")
        parts.append(f"{icon}{effect}({turns}t)")
    return " ".join(parts)


def health_bar(current: int, maximum: int) -> str:
    """Render a colored health bar string."""
    if maximum <= 0:
        return "[" + Fore.RED + "?" * BAR_LENGTH + Style.RESET_ALL + "]"
    ratio = max(0.0, min(1.0, current / maximum))
    filled = int(ratio * BAR_LENGTH)
    empty = BAR_LENGTH - filled
    if ratio > 0.5:
        color = Fore.GREEN
    elif ratio > 0.25:
        color = Fore.YELLOW
    else:
        color = Fore.RED
    bar = color + "█" * filled + Style.RESET_ALL + "░" * empty
    return f"[{bar}] {current}/{maximum}"


def show_creature(creature: Creature, show_art: bool = True) -> str:
    """Format a creature's info for display."""
    color = TYPE_COLORS.get(creature.creature_type, Fore.WHITE)
    emoji = TYPE_EMOJI.get(creature.creature_type, "")
    lines = []
    if show_art:
        art = CREATURE_ART.get(creature.name, "")
        if art:
            lines.append(art.strip())
    # Name line with nickname support
    name_display = show_creature_name(creature)
    type_display = format_types(creature)
    lines.append(f"{name_display} {type_display} Lv.{creature.level}")
    lines.append(f"  HP: {health_bar(creature.hp, creature.max_hp)}")
    status_str = format_status_effects(creature)
    if status_str:
        lines.append(f"  Status: {status_str}")
    if creature.ability:
        ability_str = show_ability(creature)
        if ability_str:
            lines.append(ability_str)
    if creature.evolution_stage > 0:
        lines.append(f"  Evolution: {'★' * creature.evolution_stage}")
    lines.append(
        f"  ATK: {creature.attack}  DEF: {creature.defense}  SPD: {creature.speed}  "
        f"XP: {creature.xp}/{creature.xp_to_next}"
    )
    return "\n".join(lines)


def battle_header(player: Creature, opponent: Creature) -> str:
    """Render the battle header showing both creatures."""
    sep = "=" * 50
    parts = [f"\n{sep}", show_creature(player, show_art=False)]
    p_status = format_status_effects(player)
    if p_status:
        parts.append(f"  Effects: {p_status}")
    parts.append("\n  VS\n")
    parts.append(show_creature(opponent, show_art=False))
    o_status = format_status_effects(opponent)
    if o_status:
        parts.append(f"  Effects: {o_status}")
    parts.append(sep)
    return "\n".join(parts)


def battle_message(text: str, msg_type: str = "info") -> str:
    """Color a battle message based on type."""
    colors = {
        "super_effective": Fore.GREEN + Style.BRIGHT,
        "not_effective": Fore.RED,
        "critical": Fore.YELLOW + Style.BRIGHT,
        "faint": Fore.RED + Style.BRIGHT,
        "level_up": Fore.CYAN + Style.BRIGHT,
        "catch": Fore.GREEN + Style.BRIGHT,
        "info": Fore.WHITE,
    }
    color = colors.get(msg_type, Fore.WHITE)
    return f"{color}{text}{Style.RESET_ALL}"


def show_menu(title: str, options: list[str]) -> str:
    """Render a numbered menu."""
    lines = [f"\n{Style.BRIGHT}{title}{Style.RESET_ALL}"]
    for i, option in enumerate(options, 1):
        lines.append(f"  {i}. {option}")
    return "\n".join(lines)


def evolution_message(old_name: str, new_name: str) -> str:
    """Format a dramatic evolution message."""
    lines = [
        "",
        battle_message("✨ " + "=" * 40 + " ✨", "level_up"),
        battle_message(f"  🧬 {old_name} is evolving!", "level_up"),
        battle_message(f"  🎉 {old_name} evolved into {new_name}!", "level_up"),
        battle_message("✨ " + "=" * 40 + " ✨", "level_up"),
        "",
    ]
    return "\n".join(lines)


def defend_message(creature_name: str) -> str:
    """Format a defend action message."""
    return battle_message(f"  🛡️ {creature_name} braces for impact!", "info")


def show_moves(creature: Creature) -> str:
    """Display a creature's available moves."""
    if not creature.moves:
        return "  No moves available!"
    lines = []
    for i, move in enumerate(creature.moves, 1):
        color = TYPE_COLORS.get(move.move_type, Fore.WHITE)
        emoji = TYPE_EMOJI.get(move.move_type, "")
        effect_tag = ""
        if move.effect:
            effect_icon = STATUS_ICONS.get(move.effect, "❓")
            chance_pct = int(move.effect_chance * 100)
            effect_tag = f" [{effect_icon}{move.effect} {chance_pct}%]"
        lines.append(
            f"  {i}. {color}{move.name}{Style.RESET_ALL} {emoji} "
            f"(Power: {move.power}) - {move.description}{effect_tag}"
        )
    return "\n".join(lines)


# -- Animated attack effects --

ATTACK_FRAMES: dict[str, list[str]] = {
    "fire":     ["  . . .",   "  🔥🔥🔥", "  💥💥💥",  "  . . ."],
    "water":    ["  ~ ~ ~",   "  💧💧💧", "  🌊🌊🌊",  "  ~ ~ ~"],
    "nature":   ["  . * .",   "  🌿🌿🌿", "  🍃🍃🍃",  "  . * ."],
    "electric": ["  . | .",   "  ⚡⚡⚡", "  💥⚡💥",  "  . | ."],
    "shadow":   ["  . . .",   "  🌑🌑🌑", "  👁🌑👁",  "  . . ."],
    "normal":   ["  . . .",   "  💫💫💫", "  💥💥💥",  "  . . ."],
    "ice":      ["  * * *",   "  ❄️❄️❄️", "  🧊🧊🧊",  "  * * *"],
    "psychic":  ["  ~ . ~",   "  🔮🔮🔮", "  ✨🔮✨",  "  ~ . ~"],
}


def animate_attack(move_type: str, delay: float = 0.15) -> None:
    """Play a brief attack animation in the terminal."""
    frames = ATTACK_FRAMES.get(move_type, ATTACK_FRAMES["normal"])
    for frame in frames:
        sys.stdout.write(f"\r{frame}")
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write("\r" + " " * 30 + "\r")
    sys.stdout.flush()


def animate_evolution(old_name: str, new_name: str, delay: float = 0.3) -> None:
    """Play an evolution animation."""
    frames = [
        f"  ✨ {old_name} is glowing!",
        f"  ✨✨ {old_name} is changing!",
        f"  ✨✨✨ Something is happening!",
        f"  🧬 {old_name} evolved into {new_name}! 🎉",
    ]
    for frame in frames:
        print(frame)
        time.sleep(delay)


def show_weather(weather_name: str, description: str) -> str:
    """Format weather display."""
    return battle_message(f"\n  🌤️ Weather: {weather_name} — {description}", "info")


def show_ability(creature: Creature) -> str:
    """Format creature ability display."""
    if not creature.ability:
        return ""
    ability_data = ABILITIES.get(creature.ability, {})
    desc = ability_data.get("description", "")
    return f"  💡 Ability: {creature.ability} — {desc}"


def format_types(creature: Creature) -> str:
    """Format creature type(s) with color and emoji."""
    primary = creature.creature_type
    p_color = TYPE_COLORS.get(primary, Fore.WHITE)
    p_emoji = TYPE_EMOJI.get(primary, "")
    result = f"{p_color}{primary}{Style.RESET_ALL} {p_emoji}"
    if creature.secondary_type:
        s_color = TYPE_COLORS.get(creature.secondary_type, Fore.WHITE)
        s_emoji = TYPE_EMOJI.get(creature.secondary_type, "")
        result += f" / {s_color}{creature.secondary_type}{Style.RESET_ALL} {s_emoji}"
    return result


def show_creature_name(creature: Creature) -> str:
    """Show creature display name (nickname or species)."""
    color = TYPE_COLORS.get(creature.creature_type, Fore.WHITE)
    name = creature.display_name
    if creature.nickname and creature.nickname != creature.name:
        return f"{color}{name}{Style.RESET_ALL} ({creature.name})"
    return f"{color}{name}{Style.RESET_ALL}"


def show_item(name: str, item_data: dict, qty: int = 0) -> str:
    """Format an item for display."""
    desc = item_data.get("description", "")
    price = item_data.get("price", 0)
    qty_str = f" x{qty}" if qty > 0 else ""
    return f"  {name}{qty_str} — {desc} (💰{price}g)"


def show_inventory(items: dict[str, int], gold: int) -> str:
    """Format full inventory display."""
    from data import ITEMS
    lines = [f"\n{Style.BRIGHT}🎒 Inventory{Style.RESET_ALL} (💰 {gold}g)"]
    if not items:
        lines.append("  (empty)")
    else:
        for name, qty in sorted(items.items()):
            item_data = ITEMS.get(name, {})
            desc = item_data.get("description", "")
            lines.append(f"  • {name} x{qty} — {desc}")
    return "\n".join(lines)


def show_achievement_unlock(achievement: dict) -> str:
    """Format a newly unlocked achievement."""
    icon = achievement.get("icon", "🏆")
    name = achievement.get("name", "")
    desc = achievement.get("description", "")
    lines = [
        "",
        battle_message(f"  {icon} ═══ ACHIEVEMENT UNLOCKED ═══ {icon}", "level_up"),
        battle_message(f"  {icon} {name}", "level_up"),
        battle_message(f"  {desc}", "info"),
        "",
    ]
    return "\n".join(lines)


def show_tournament_header(tier_name: str, current_round: int, total_rounds: int) -> str:
    """Format tournament progress header."""
    bar_filled = current_round
    bar_empty = total_rounds - current_round
    progress = "🏆" * bar_filled + "⬜" * bar_empty
    return f"\n  🏟️ {tier_name} — Round {current_round}/{total_rounds}\n  {progress}"


def show_chapter_intro(chapter: dict) -> str:
    """Format a story chapter introduction."""
    lines = [
        "",
        battle_message(f"  📖 ═══ Chapter {chapter['id']}: {chapter['title']} ═══", "level_up"),
        "",
        f"  {chapter['intro']}",
        "",
        battle_message(f"  {chapter['boss_intro']}", "critical"),
        "",
    ]
    return "\n".join(lines)


def show_breeding_result(offspring: object) -> str:
    """Format breeding result display."""
    c = offspring  # type: ignore
    lines = [
        "",
        battle_message("  🥚 ═══ NEW CREATURE HATCHED ═══ 🥚", "catch"),
        f"  {c.name}",  # type: ignore
        f"  Type: {c.creature_type}",  # type: ignore
    ]
    if hasattr(c, 'secondary_type') and c.secondary_type:  # type: ignore
        lines[-1] += f" / {c.secondary_type}"  # type: ignore
    if hasattr(c, 'ability') and c.ability:  # type: ignore
        lines.append(f"  Ability: {c.ability}")  # type: ignore
    lines.append("")
    return "\n".join(lines)


def show_trade_code(code: str) -> str:
    """Format a trade code for display."""
    lines = [
        "",
        battle_message("  📤 ═══ TRADE CODE ═══", "info"),
        f"  {code}",
        battle_message("  Share this code to trade your creature!", "info"),
        "",
    ]
    return "\n".join(lines)
