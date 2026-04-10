"""Story / quest mode progression."""
from __future__ import annotations

from data import STORY_CHAPTERS, get_moves_for_types
from creature import Creature


class StoryProgress:
    """Tracks the player's progress through story chapters."""

    def __init__(self) -> None:
        self.current_chapter: int = 1
        self.completed_chapters: set[int] = set()
        self.story_complete: bool = False

    def get_current_chapter(self) -> dict | None:
        """Return the current chapter data, or None if all chapters are complete."""
        for ch in STORY_CHAPTERS:
            if ch["id"] == self.current_chapter:
                return ch
        return None

    def get_chapter_intro(self) -> str:
        """Formatted intro text for the current chapter."""
        chapter = self.get_current_chapter()
        if chapter is None:
            return "All chapters complete!"
        return f"Chapter {chapter['id']}: {chapter['title']}\n{chapter['intro']}"

    def create_boss(self) -> Creature:
        """Create the boss creature for the current chapter with 50% bonus HP."""
        chapter = self.get_current_chapter()
        if chapter is None:
            raise RuntimeError("No current chapter available")
        boss_data = chapter["boss"]
        level = boss_data["level"]
        tier = 1 if level <= 6 else 2
        moves = get_moves_for_types(boss_data["moves"], tier=tier)
        boss = Creature(
            name=boss_data["name"],
            creature_type=boss_data["creature_type"],
            level=level,
            moves=moves,
        )
        # Give boss 50% more HP
        bonus = boss.max_hp // 2
        boss.max_hp += bonus
        boss.hp = boss.max_hp
        return boss

    def complete_chapter(self) -> dict:
        """Mark current chapter complete and advance. Returns the completed chapter dict."""
        chapter = self.get_current_chapter()
        if chapter is None:
            raise RuntimeError("No current chapter to complete")
        self.completed_chapters.add(self.current_chapter)
        self.current_chapter += 1
        if len(self.completed_chapters) >= len(STORY_CHAPTERS):
            self.story_complete = True
        return chapter

    def is_chapter_available(self) -> bool:
        """True if there are incomplete chapters remaining."""
        return not self.story_complete

    def get_progress_summary(self) -> str:
        """Formatted progress summary."""
        chapter = self.get_current_chapter()
        if chapter is None:
            return "📖 Story: Complete!"
        total = len(STORY_CHAPTERS)
        return f"📖 Story: Chapter {chapter['id']}/{total} — {chapter['title']}"

    def to_dict(self) -> dict:
        return {
            "current_chapter": self.current_chapter,
            "completed_chapters": sorted(self.completed_chapters),
            "story_complete": self.story_complete,
        }

    @classmethod
    def from_dict(cls, data: dict) -> StoryProgress:
        progress = cls()
        progress.current_chapter = data.get("current_chapter", 1)
        progress.completed_chapters = set(data.get("completed_chapters", []))
        progress.story_complete = data.get("story_complete", False)
        return progress
