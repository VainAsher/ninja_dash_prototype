"""High Scores Module - Local JSON persistence for top scores."""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict

from save_paths import get_save_path


HIGHSCORES_FILE = "highscores.json"
MAX_SCORES = 10


@dataclass
class HighscoreEntry:
    name: str
    score: int
    level: int
    difficulty: str
    timestamp: str

    @classmethod
    def from_dict(cls, data: Dict) -> "HighscoreEntry":
        return cls(
            name=str(data.get("name", "Player")),
            score=int(data.get("score", 0)),
            level=int(data.get("level", 1)),
            difficulty=str(data.get("difficulty", "normal")),
            timestamp=str(
                data.get(
                    "timestamp",
                    datetime.utcnow().isoformat(timespec="seconds"),
                )
            ),
        )

    def to_dict(self) -> Dict:
        return asdict(self)


def _scores_path():
    return get_save_path(HIGHSCORES_FILE)


def load_highscores() -> List[Dict]:
    path = _scores_path()
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
    entries = [HighscoreEntry.from_dict(item) for item in raw]
    entries.sort(key=lambda e: e.score, reverse=True)
    return [e.to_dict() for e in entries]


def save_highscores(scores: List[Dict]) -> None:
    path = _scores_path()
    entries = [HighscoreEntry.from_dict(s) for s in scores]
    entries.sort(key=lambda e: e.score, reverse=True)
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump([e.to_dict() for e in entries], f, indent=2)
    except OSError:
        pass


def qualifies_for_highscore(score: int) -> bool:
    scores = load_highscores()
    if len(scores) < MAX_SCORES:
        return True
    lowest = min(scores, key=lambda s: s.get("score", 0))
    return score >= lowest.get("score", 0)


def add_highscore(name: str, score: int, level: int, difficulty: str) -> int:
    if not qualifies_for_highscore(score):
        return -1
    scores = [HighscoreEntry.from_dict(s) for s in load_highscores()]
    entry = HighscoreEntry(
        name=name,
        score=score,
        level=level,
        difficulty=difficulty,
        timestamp=datetime.utcnow().isoformat(timespec="seconds"),
    )
    scores.append(entry)
    scores.sort(key=lambda e: e.score, reverse=True)
    scores = scores[:MAX_SCORES]
    save_highscores([e.to_dict() for e in scores])
    for idx, e in enumerate(scores, start=1):
        if (
            e.name == entry.name
            and e.score == entry.score
            and e.level == entry.level
            and e.difficulty == entry.difficulty
        ):
            return idx
    return -1


def get_highscores() -> List[Dict]:
    return load_highscores()


def clear_highscores() -> None:
    path = _scores_path()
    try:
        if path.exists():
            path.unlink()
    except OSError:
        pass
