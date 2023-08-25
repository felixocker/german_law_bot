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
    LAWS,
    OPENAI_EF,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_and_unzip(url: str, destination: str) -> None:
    http_response = urlopen(url)
    zipfile = ZipFile(BytesIO(http_response.read()))
    zipfile.extractall(path=destination)
    logger.info("Download done.")


@dataclass
class Paragraph:
    law: str
    par: str
    title: str
    text: str
    footnotes: str


def extract_xmls(source: str) -> List[Paragraph]:
    # TODO: possibly combine sub-laws into one chunk
    files = [os.path.join(source, f) for f in os.listdir(source) if f.endswith(".xml")]
    res = []
    for f in files:
        tree = ET.parse(f)
        root = tree.getroot()
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
            if valid:
                par = Paragraph(law=law, par=par, title=title, text=text, footnotes=footnotes)
                res.append(par)
            else:
                continue
    logger.info(f"Extracted {len(res)} (sub)paragraphs.")
    return res


def chunk_paragraphs(
    parags: List[Paragraph],
    max_chunk: int = 16_000,
    overlap: int = 500
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
                chunk_start = i*chunk_length - (i > 0) * overlap
                chunk_end = (i+1) * chunk_length + overlap
                parags_.append(Paragraph(
                    law=p.law,
                    par=p.par+f" Teil {i+1}",
                    title=p.title+f" Teil {i+1}",
                    text=p.text[chunk_start:chunk_end],
                    footnotes=p.footnotes
                ))
            logger.info(f"Split up {p.par} into {parts} parts due to its length of {text_len}.")
    return parags_


def load_into_chroma(parags: List[Paragraph]) -> None:
    chroma_client = chromadb.PersistentClient(path="../data/chroma")
    collection = chroma_client.get_or_create_collection(name="laws", embedding_function=OPENAI_EF)
    collection.add(
        documents=[p.title + "\n\n" + p.text for p in parags],
        metadatas=[{"law": p.law, "paragraph": p.par, "title": p.title} for p in parags],
        ids=[p.law + p.par.replace("§", "").replace(" ", "_") for p in parags]
    )
    logger.info(f"Loaded {len(parags)} paragraphs into the vector store.")


def peek() -> None:
    chroma_client = chromadb.PersistentClient(path="../data/chroma")
    collection = chroma_client.get_or_create_collection(name="laws", embedding_function=OPENAI_EF)
    print(collection.peek())


def main():
    downloads_folder = "../data/downloads/"
    for law in LAWS:
        download_and_unzip(url=LAWS[law], destination=downloads_folder)
        logger.info(f"Retrieved {law}.")
    parags = extract_xmls(source=downloads_folder)
    chunked_parags = chunk_paragraphs(parags)
    load_into_chroma(chunked_parags)
    peek()


if __name__ == "__main__":
    main()
