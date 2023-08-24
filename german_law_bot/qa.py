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


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def retrieve_from_vdb(query: str, n: int = 3) -> dict:
    chroma_client = chromadb.PersistentClient(path="../data/chroma")
    collection = chroma_client.get_or_create_collection(name="laws", embedding_function=OPENAI_EF)
    relevant_chunks = collection.query(
        query_texts=[query],
        n_results=n,
    )
    logger.info(f"Most relevant chunks for query `{query}` are {relevant_chunks['ids']}")
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
) -> str:
    """Answer query using Retrieval Augmented Generation.
    Use map reduce if the number of chunks to be considered is set to be larger than 1.
    """
    chunks_ = retrieve_from_vdb(query=query, n=n_results)
    sources = chunks_["ids"][0]
    if n_results == 1:
        context = chunks_["documents"][0][0]
        prompt = PROMPT_RAG.replace("<context>", context).replace("<question>", query)
    elif n_results > 1:
        context = {}
        irrelevant_srcs = []
        for i in range(n_results):
            context_single = chunks_["documents"][0][i]
            prompt = PROMPT_MAP_REDUCE.replace("<context>", context_single).replace("<question>", query)
            msgs = [{"role": "user", "content": prompt}]
            res = query_llm(msgs, model)
            if res.strip().lower() == "irrelevant":
                irrelevant_srcs.append(sources[i])
                continue
            context[sources[i]] = res
        sources = [s for s in sources if s not in irrelevant_srcs]
        context_summary = "\n".join([src+": "+txt for src, txt in context.items()])
        prompt = PROMPT_MAP_REDUCE_SUMMARY.replace("<context>", context_summary).replace("<question>", query)
    else:
        raise ValueError(f"n_results must be >= 0.")
    msgs = [{"role": "user", "content": prompt}]
    res = query_llm(msgs, model)
    logger.info(f"Got response: {res}.")
    return res + f"\n\nQuelle: {','.join(sources)}"


if __name__ == "__main__":
    example = (
        "Gilt die Überführung eines Wirtschaftsguts in das Privatvermögen "
        "des Steuerpflichtigen durch Entnahme als Anschaffung?"
    )
    mr = rag_query(query=example, n_results=3)
    print(mr)
