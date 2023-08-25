#!/usr/bin/env python3
"""Generic utilities"""
from typing import List

import openai

from constants import EMBEDDING_MODEL


def get_embedding(text: str, model: str = EMBEDDING_MODEL) -> List[float]:
    return openai.Embedding.create(input=[text], model=model)["data"][0]["embedding"]
