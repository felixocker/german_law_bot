#!/usr/bin/env python3
"""Module for keeping track of interactions"""

import logging
import os
import shelve

from dataclasses import dataclass
from typing import Optional

from constants import PERSISTENT_HISTORY


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QuestionAnswerEntry:
    question: str
    context_summary: str
    answer: str
    laws: Optional[list[str]] = None


@dataclass
class StudyBuddyEntry:
    topic: str
    source: str
    question: str
    answer: str
    explanation: str
    assessment: Optional[bool] = None


def store(entry: StudyBuddyEntry | QuestionAnswerEntry) -> None:
    if isinstance(entry, StudyBuddyEntry):
        entry_type = "studdybuddy"
    elif isinstance(entry, QuestionAnswerEntry):
        entry_type = "qabot"
    else:
        raise TypeError(f"Unexpected input {type(entry)}.")
    logging.info(f"Storing entry {entry} of type {entry_type}.")
    with shelve.open(PERSISTENT_HISTORY, writeback=True) as db:
        if entry_type not in db:
            db[entry_type] = [entry]
        else:
            db[entry_type].append(entry)


def inspect(entry_type: str = "studdybuddy"):
    with shelve.open(PERSISTENT_HISTORY) as db:
        if entry_type not in db:
            return "Nothing to show."
        return db[entry_type]


def reset() -> None:
    """Deletes entire history. Use with CAUTION."""
    os.remove(PERSISTENT_HISTORY)


if __name__ == "__main__":
    # store(QuestionAnswerEntry("test", "test", "test"))
    print(*inspect(), sep="\n")