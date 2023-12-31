#!/usr/bin/env python3
"""Retrieve laws, load into vector store."""
import logging
import os

from typing import (
    List,
)
from dataclasses import dataclass

import chromadb
import xml.etree.ElementTree as ET

from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile

from constants import (
    CHROMA_DIR,
    COLLECTION_NAME,
    DOWNLOADS_DIR,
    OPENAI_EF,
)
from utils import (
    get_embedding,
    load_settings,
    save_settings,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_and_unzip(url: str, destination: str) -> str:
    http_response = urlopen(url)
    zipfile = ZipFile(BytesIO(http_response.read()))
    zipfile.extractall(path=destination)
    logger.info("Download done.")
    files_ = [f for f in zipfile.namelist() if f.endswith(".xml")]
    print(files_)
    assert len(files_) == 1, "Download does not contain exactly one XML."
    return files_[0]


@dataclass
class Paragraph:
    law: str
    par: str
    title: str
    text: str
    footnotes: str
    version_info: str
    embedding: List[float] = None


def extract_xml(source_dir: str, source_file: str) -> List[Paragraph]:
    # TODO: possibly combine sub-laws into one chunk
    f = os.path.join(source_dir, source_file)
    res = []
    tree = ET.parse(f)
    root = tree.getroot()
    version_info = tree.findall(".//standkommentar")
    version_info = " ".join([vi.text for vi in version_info])
    logger.info(f"Version info for {source_file}: {version_info}")
    for norm in root:
        valid = True
        law, par, title, text, footnotes = None, None, None, None, None
        for child in norm:
            subtags = [c.tag for c in child]
            if child.tag == "metadaten":
                if all(t in subtags for t in ("jurabk", "enbez", "titel")):
                    for md in child:
                        if md.tag == "jurabk":
                            law = md.text
                        if md.tag == "enbez":
                            par = md.text
                        if md.tag == "titel":
                            title = " ".join(list(md.itertext()))
                else:
                    valid = False
            if child.tag == "textdaten":
                if "text" in subtags:
                    for cont in child:
                        if cont.tag == "text":
                            text = " ".join(list(cont.itertext()))
                        if cont.tag == "fussnoten":
                            footnotes = " ".join(list(cont.itertext()))
                else:
                    valid = False
            if not title and not text:
                valid = False
        if valid:
            par = Paragraph(
                law=law,
                par=par,
                title=title,
                text=text,
                version_info=version_info,
                footnotes=footnotes,
            )
            res.append(par)
        else:
            continue
    logger.info(f"Extracted {len(res)} (sub)paragraphs from {source_file}.")
    return res


def chunk_paragraphs(
    parags: List[Paragraph], max_chunk: int = 16_000, overlap: int = 500
) -> List[Paragraph]:
    # NOTE: this is a very pragmatic approach to chunking
    parags_ = []
    for p in parags:
        text_len = len(p.text)
        if text_len < max_chunk:
            parags_.append(p)
        else:
            parts = text_len // (max_chunk + overlap) + 1
            chunk_length = text_len // parts
            for i in range(parts):
                chunk_start = i * chunk_length - (i > 0) * overlap
                chunk_end = (i + 1) * chunk_length + overlap
                parags_.append(
                    Paragraph(
                        law=p.law,
                        par=p.par + f" Teil {i+1}",
                        title=p.title + f" Teil {i+1}",
                        text=p.text[chunk_start:chunk_end],
                        version_info=p.version_info,
                        footnotes=p.footnotes,
                    )
                )
            logger.info(
                f"Split up {p.par} into {parts} parts due to its length of {text_len}."
            )
    return parags_


def embed_paragraphs(
    parags: List[Paragraph],
) -> List[Paragraph]:
    ln = len(parags)
    for c, p in enumerate(parags):
        p.embedding = get_embedding(p.title + "\n\n" + p.text)
        logger.info(f"Embedding {c}/{ln}: {p}")
    return parags


def load_into_chroma(parags: List[Paragraph]) -> None:
    chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=OPENAI_EF
    )
    collection.add(
        documents=[p.title + "\n\n" + p.text for p in parags],
        embeddings=[p.embedding for p in parags],
        metadatas=[
            {"law": p.law, "paragraph": p.par, "title": p.title} for p in parags
        ],
        ids=[p.law + p.par.replace("§", "").replace(" ", "_") for p in parags],
    )
    logger.info(f"Loaded {len(parags)} paragraphs into the vector store.")


def delete_from_chroma(law_code: str) -> None:
    chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=OPENAI_EF
    )
    del_len = len(collection.get(where={"law": law_code}))
    collection.delete(where={"law": law_code})
    logger.info(f"Deleted {del_len} elements from the vector store for {law_code}.")


def get_chroma_stats() -> str:
    chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=OPENAI_EF
    )
    return "Anzahl an Embeddings im Vector Store: " + str(collection.count())


def peek() -> None:
    chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=OPENAI_EF
    )
    print(collection.peek())


def load_from_config() -> None:
    config = load_settings()
    for law in config:
        if config[law]["desired"] is True and config[law]["loaded"] is False:
            filename = download_and_unzip(
                url=config[law]["link"], destination=DOWNLOADS_DIR
            )
            parags = extract_xml(source_dir=DOWNLOADS_DIR, source_file=filename)
            chunked_parags = chunk_paragraphs(parags)
            embedded_parags = embed_paragraphs(chunked_parags)
            logger.info(f"Retrieved {law}.")
            load_into_chroma(embedded_parags)
            logger.info(f"Loaded {law} into vector store.")
            config[law]["loaded"] = True
            config[law]["file"] = filename
            save_settings(config)


if __name__ == "__main__":
    load_from_config()
    peek()
