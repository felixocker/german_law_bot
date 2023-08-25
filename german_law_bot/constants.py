#!/usr/bin/env python3
"""Relevant constants"""
import os
from chromadb.utils import embedding_functions


LAWS = {
    "ESTG_XML": "https://www.gesetze-im-internet.de/estg/xml.zip",
    # "BGB_XML": "https://www.gesetze-im-internet.de/bgb/xml.zip",
}
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-ada-002"

OPENAI_EF = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY,
    model_name=EMBEDDING_MODEL
)
