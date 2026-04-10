"""Display utilities: health bars, ASCII art, colored terminal output."""
from __future__ import annotations

from colorama import Fore, Style, init as colorama_init

from creature import Creature
from data import CREATURE_ART

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
    lines.append(
        f"{color}{creature.name}{Style.RESET_ALL} {emoji} "
        f"Lv.{creature.level}"
    )
    lines.append(f"  HP: {health_bar(creature.hp, creature.max_hp)}")
    status_str = format_status_effects(creature)
    if status_str:
        lines.append(f"  Status: {status_str}")
    if creature.evolution_stage > 0:
        lines.append(f"  Evolution: {'★' * creature.evolution_stage}")
    lines.append(
        f"  ATK: {creature.attack}  DEF: {creature.defense}  "
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
