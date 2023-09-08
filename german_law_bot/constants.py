#!/usr/bin/env python3
"""Relevant constants"""
import os
from chromadb.utils import embedding_functions


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY is None:
    raise ValueError(
        "Please set an environment variable for your OpenAI API key. See "
        "https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety"
    )
EMBEDDING_MODEL = "text-embedding-ada-002"

CONFIG = "config.yaml"
DOWNLOADS = "../data/downloads/"

COLLECTION_NAME = "laws"

OPENAI_EF = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY, model_name=EMBEDDING_MODEL
)

AUTO_LAUNCH_BROWSER: bool = True
