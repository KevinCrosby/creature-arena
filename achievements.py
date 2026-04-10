from __future__ import annotations

from data import ACHIEVEMENT_DEFS, ENCOUNTER_TABLES

# Condition map: achievement_id -> (stat_name, threshold)
_CONDITIONS: dict[str, tuple[str, int]] = {
    "first_catch": ("creatures_caught", 1),
    "catch_10": ("creatures_caught", 10),
    "win_first_battle": ("battles_won", 1),
    "win_10_battles": ("battles_won", 10),
    "win_50_battles": ("battles_won", 50),
    "first_evolution": ("evolutions", 1),
    "full_party": ("max_party_size", 6),
    "level_10": ("max_level", 10),
    "all_types": ("types_caught", 7),
    "no_damage_win": ("no_damage_wins", 1),
    "crit_finish": ("crit_finishes", 1),
    "first_breed": ("breeds", 1),
    "tournament_win": ("tournaments_won", 1),
    "story_complete": ("chapters_complete", 5),
    "all_areas": ("areas_visited", len(ENCOUNTER_TABLES)),
}


class AchievementTracker:
    """Tracks achievement unlocks and associated stat counters."""

    def __init__(self) -> None:
        self.unlocked: dict[str, bool] = {a["id"]: False for a in ACHIEVEMENT_DEFS}
        self.stats: dict[str, int] = {stat: 0 for _, (stat, _) in _CONDITIONS.items()}

    # -- Stat helpers ------------------------------------------------------

    def increment_stat(self, stat: str, amount: int = 1) -> None:
        self.stats[stat] = self.stats.get(stat, 0) + amount

    def get_stat(self, stat: str) -> int:
        return self.stats.get(stat, 0)

    # -- Unlock helpers ----------------------------------------------------

    def unlock(self, achievement_id: str) -> bool:
        if self.unlocked.get(achievement_id):
            return False
        self.unlocked[achievement_id] = True
        return True

    def is_unlocked(self, achievement_id: str) -> bool:
        return self.unlocked.get(achievement_id, False)

    # -- Condition checking ------------------------------------------------

    def check_achievements(self) -> list[dict]:
        newly_unlocked: list[dict] = []
        for achievement in ACHIEVEMENT_DEFS:
            aid = achievement["id"]
            if self.unlocked.get(aid):
                continue
            condition = _CONDITIONS.get(aid)
            if condition is None:
                continue
            stat_name, threshold = condition
            if self.stats.get(stat_name, 0) >= threshold:
                self.unlocked[aid] = True
                newly_unlocked.append(achievement)
        return newly_unlocked

    # -- Query helpers -----------------------------------------------------

    def get_unlocked(self) -> list[dict]:
        return [a for a in ACHIEVEMENT_DEFS if self.unlocked.get(a["id"])]

    def get_progress_summary(self) -> str:
        total = len(ACHIEVEMENT_DEFS)
        count = sum(1 for v in self.unlocked.values() if v)
        return f"\U0001f3c6 Achievements: {count}/{total} unlocked"

    # -- Serialisation -----------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "unlocked": self.unlocked,
            "stats": self.stats,
        }

    @classmethod
    def from_dict(cls, data: dict) -> AchievementTracker:
        tracker = cls()
        tracker.unlocked.update(data.get("unlocked", {}))
        tracker.stats.update(data.get("stats", {}))
        return tracker
