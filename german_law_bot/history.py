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
    model: str
    question: str
    context_summary: str
    answer: str
    laws: Optional[list[str]] = None


@dataclass
class StudyBuddyEntry:
    model: str
    topic: str
    source: str
    question: str
    answer: str
    explanation: str
    assessment: Optional[bool] = None


def store(entry: StudyBuddyEntry | QuestionAnswerEntry) -> None:
    if isinstance(entry, StudyBuddyEntry):
        entry_type = "studybuddy"
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


def retrieve(entry_type: str = "studybuddy"):
    with shelve.open(PERSISTENT_HISTORY) as db:
        if entry_type not in db:
            logger.warning(f"Invalid key {entry_type} for looking up history.")
            return []
        return db[entry_type]


def reset() -> None:
    """Deletes entire history. Use with CAUTION."""
    os.remove(PERSISTENT_HISTORY)
