#!/usr/bin/env python3
"""Relevant constants"""
import os
from chromadb.utils import embedding_functions


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-ada-002"

CONFIG = "config.yaml"
DOWNLOADS = "../data/downloads/"

OPENAI_EF = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY,
    model_name=EMBEDDING_MODEL
)
