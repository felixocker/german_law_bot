#!/usr/bin/env python3
"""Generic utilities"""
import logging
from typing import List
import yaml

from openai import OpenAI

from constants import (
    CONFIG,
    EMBEDDING_MODEL,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


oai_client = OpenAI()


def get_embedding(text: str, model: str = EMBEDDING_MODEL) -> List[float]:
    return oai_client.embeddings.create(input=[text], model=model).data[0].embedding


def load_settings(config: str = CONFIG) -> dict:
    with open(config, "r") as f:
        conf = yaml.safe_load(f)
    logger.info("Loaded config from file.")
    return conf


def save_settings(data: dict, config: str = CONFIG) -> None:
    with open(config, "w") as f:
        yaml.dump(data, f, default_flow_style=False)
    logger.info("Updated config with current status.")
