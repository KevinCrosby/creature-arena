"""Battle replay recording and playback."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone


class BattleReplay:
    """Records events from a single battle for later playback."""

    def __init__(self, player_name: str, opponent_name: str) -> None:
        self.player_name = player_name
        self.opponent_name = opponent_name
        self.events: list[dict] = []
        self.timestamp: str = datetime.now(timezone.utc).isoformat()
        self.result: str | None = None

    # -- Event recording -------------------------------------------------- #

    def record_event(self, event_type: str, data: dict) -> None:
        """Append a generic battle event."""
        self.events.append({"type": event_type, **data})

    def record_attack(
        self,
        attacker: str,
        move_name: str,
        damage: int,
        is_crit: bool,
        type_mult: float,
        effect: str | None,
    ) -> None:
        self.record_event("attack", {
            "attacker": attacker,
            "move": move_name,
            "damage": damage,
            "is_crit": is_crit,
            "type_mult": type_mult,
            "effect": effect,
        })

    def record_defend(self, creature_name: str) -> None:
        self.record_event("defend", {"creature": creature_name})

    def record_status(self, creature_name: str, effect: str, damage: int) -> None:
        self.record_event("status_effect", {
            "creature": creature_name,
            "effect": effect,
            "damage": damage,
        })

    # -- Result ----------------------------------------------------------- #

    def set_result(self, winner: str) -> None:
        """Set the battle result based on whether *winner* is the player."""
        self.result = "win" if winner == self.player_name else "loss"

    def get_summary(self) -> str:
        """One-line summary suitable for display in a replay list."""
        result_str = self.result.capitalize() + "!" if self.result else "Incomplete"
        turns = len([e for e in self.events if e["type"] in ("attack", "defend")])
        return (
            f"⚔️ {self.player_name} vs {self.opponent_name} — "
            f"{result_str} ({turns} turn{'s' if turns != 1 else ''})"
        )

    # -- Serialization ---------------------------------------------------- #

    def to_dict(self) -> dict:
        return {
            "player_name": self.player_name,
            "opponent_name": self.opponent_name,
            "events": self.events,
            "timestamp": self.timestamp,
            "result": self.result,
        }

    @classmethod
    def from_dict(cls, data: dict) -> BattleReplay:
        replay = cls(data["player_name"], data["opponent_name"])
        replay.events = data.get("events", [])
        replay.timestamp = data.get("timestamp", replay.timestamp)
        replay.result = data.get("result")
        return replay


class ReplayManager:
    """Persist and retrieve battle replays on disk."""

    REPLAY_DIR = os.path.expanduser("~/.creature-arena/replays")

    def __init__(self) -> None:
        self.replays: list[BattleReplay] = []

    def save_replay(self, replay: BattleReplay) -> None:
        """Save a single replay to a JSON file in REPLAY_DIR."""
        os.makedirs(self.REPLAY_DIR, exist_ok=True)
        safe_ts = replay.timestamp.replace(":", "-")
        filename = f"replay_{safe_ts}.json"
        path = os.path.join(self.REPLAY_DIR, filename)
        with open(path, "w") as f:
            json.dump(replay.to_dict(), f, indent=2)

    def load_replays(self) -> list[BattleReplay]:
        """Load all replays from disk, sorted newest-first, capped at 20."""
        self.replays = []
        if not os.path.isdir(self.REPLAY_DIR):
            return self.replays
        for name in os.listdir(self.REPLAY_DIR):
            if not name.endswith(".json"):
                continue
            path = os.path.join(self.REPLAY_DIR, name)
            try:
                with open(path) as f:
                    data = json.load(f)
                self.replays.append(BattleReplay.from_dict(data))
            except Exception:
                continue
        self.replays.sort(key=lambda r: r.timestamp, reverse=True)
        self.replays = self.replays[:20]
        return self.replays

    def get_replay_list(self) -> list[str]:
        """Return summary strings for all loaded replays."""
        return [r.get_summary() for r in self.replays]

    @staticmethod
    def playback(replay: BattleReplay) -> list[str]:
        """Return formatted event strings for text-based playback."""
        lines: list[str] = []
        for event in replay.events:
            etype = event.get("type", "unknown")
            if etype == "attack":
                crit = " 💥 CRIT!" if event.get("is_crit") else ""
                mult = event.get("type_mult", 1.0)
                eff = ""
                if mult > 1.0:
                    eff = " (super effective!)"
                elif mult < 1.0:
                    eff = " (not very effective)"
                effect_str = f" → {event['effect']}" if event.get("effect") else ""
                lines.append(
                    f"⚔️ {event['attacker']} used {event['move']}! "
                    f"{event['damage']} dmg{crit}{eff}{effect_str}"
                )
            elif etype == "defend":
                lines.append(f"🛡️ {event['creature']} is defending!")
            elif etype == "status_effect":
                lines.append(
                    f"🔥 {event['creature']} took {event['damage']} "
                    f"damage from {event['effect']}!"
                )
            elif etype == "weather_change":
                lines.append(f"🌦️ Weather changed to {event.get('weather', '?')}!")
            elif etype == "faint":
                lines.append(f"💀 {event.get('creature', '?')} fainted!")
            elif etype == "level_up":
                lines.append(
                    f"⬆️ {event.get('creature', '?')} leveled up to "
                    f"Lv.{event.get('level', '?')}!"
                )
            elif etype == "evolution":
                lines.append(
                    f"✨ {event.get('creature', '?')} evolved into "
                    f"{event.get('new_form', '?')}!"
                )
            else:
                lines.append(f"▶ {etype}: {event}")
        return lines
