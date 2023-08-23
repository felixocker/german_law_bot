#!/usr/bin/env python3
"""insert docstring here"""
import chromadb
from chromadb.utils import embedding_functions

from constants import (
    EMBEDDING_MODEL,
    OPENAI_API_KEY,
)


def main(query: str):
    chroma_client = chromadb.PersistentClient(path="../data/chroma")
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=OPENAI_API_KEY,
        model_name=EMBEDDING_MODEL
    )
    collection = chroma_client.get_or_create_collection(name="laws", embedding_function=openai_ef)
    relevant_chunks = collection.query(
        query_texts=[query],
        n_results=3,
    )
    return relevant_chunks


if __name__ == "__main__":
    example = (
        "Gilt die Überführung eines Wirtschaftsguts in das Privatvermögen "
        "des Steuerpflichtigen durch Entnahme als Anschaffung?"
    )
    print(main(query=example))
