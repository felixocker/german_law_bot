#!/usr/bin/env python3
"""Core QA, including RAG and map-reduce"""
from __future__ import annotations

import logging

import chromadb
import openai

from typing import (
    List,
    Dict,
)

from constants import OPENAI_EF
from prompts.prompt_qa import (
    PROMPT_MAP_REDUCE,
    PROMPT_MAP_REDUCE_SUMMARY,
    PROMPT_RAG,
)
from utils import get_embedding


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def retrieve_from_vdb(
    query: str,
    where_filter: dict,
    n: int = 3,
) -> dict:
    query_embedding = get_embedding(query)
    chroma_client = chromadb.PersistentClient(path="../data/chroma")
    collection = chroma_client.get_or_create_collection(
        name="laws", embedding_function=OPENAI_EF
    )
    relevant_chunks = collection.query(
        query_embeddings=[query_embedding],
        n_results=n,
        where=where_filter,
    )
    logger.info(
        f"Most relevant chunks for query `{query}` are {relevant_chunks['ids']}"
    )
    return relevant_chunks


def query_llm(
    msgs: List[Dict[str, str]],
    model: str = "gpt-3.5-turbo",
) -> str:
    logger.info(f"Sending query: {msgs}.")
    response = None
    while not response:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=msgs,
                temperature=0,
            )
        except openai.error.APIError as e:
            logger.error(e)
        except openai.error.RateLimitError as e:
            logger.error(e)
        except openai.error.ServiceUnavailableError as e:
            logger.error(e)
    res = response.choices[0].message.content
    logger.info(f"Received response to query: `{res}`.")
    return res


def rag_query(
    query: str,
    model: str = "gpt-3.5-turbo",
    n_results: int = 3,
    law_filter: List[str] = None,
) -> str:
    """Answer query using Retrieval Augmented Generation.
    Use map reduce if the number of chunks to be considered is set to be larger than 1.
    """
    if not law_filter:
        law_filter = {}
    elif len(law_filter) == 1:
        law_filter = {"law": law_filter[0]}
    else:
        law_filter = {"$or": [{"law": lf} for lf in law_filter]}
    chunks_ = retrieve_from_vdb(query=query, n=n_results, where_filter=law_filter)
    sources = chunks_["ids"][0]
    irrelevant_srcs = None
    if n_results == 1:
        context = chunks_["documents"][0][0]
        prompt = PROMPT_RAG.format(context=context, question=query)
    elif n_results > 1:
        context = {}
        irrelevant_srcs = []
        for i in range(n_results):
            context_single = chunks_["documents"][0][i]
            prompt = PROMPT_MAP_REDUCE.format(context=context_single, question=query)
            msgs = [{"role": "user", "content": prompt}]
            res = query_llm(msgs, model)
            if res.strip().lower() == "irrelevant":
                irrelevant_srcs.append(sources[i])
                continue
            context[sources[i]] = res
        sources = [s for s in sources if s not in irrelevant_srcs]
        if not sources:
            return (
                f"Keine relevanten Informationen verfuegbar"
                f"(geprueft: {', '.join(irrelevant_srcs)})."
            )
        else:
            context_summary = "\n".join(
                [src + ": " + txt for src, txt in context.items()]
            )
        prompt = PROMPT_MAP_REDUCE_SUMMARY.format(
            context=context_summary,
            question=query,
        )
    else:
        raise ValueError(f"n_results must be >= 0 but is {n_results}.")
    msgs = [{"role": "user", "content": prompt}]
    res = query_llm(msgs, model)
    logger.info(f"Got response: `{res}`.")
    response = res + f"\n\nQuelle: {', '.join(sources)}"
    if irrelevant_srcs:
        response += f" (Auch geprueft: {', '.join(irrelevant_srcs)})"
    return response


if __name__ == "__main__":
    while True:
        question = input("FRAGE: ")
        if question == "quit":
            break
        mr = rag_query(query=question, n_results=5)
        print("ANTWORT:\n" + mr)
    # Example:
    # Gilt die Überführung eines Wirtschaftsguts in das Privatvermögen des
    # Steuerpflichtigen durch Entnahme als Anschaffung?
