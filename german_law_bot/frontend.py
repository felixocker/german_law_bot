#!/usr/bin/env python3
"""Gradio frontend"""
import logging
import time

import gradio as gr

from ingest import (
    load_from_config,
    delete_from_chroma,
)
from qa import rag_query
from utils import (
    load_settings,
    save_settings,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def echo(message, history, n_results, law_filter):
    response = rag_query(query=message, n_results=n_results, law_filter=law_filter)
    for i, _ in enumerate(response):
        time.sleep(0.02)
        yield response[: i + 1]


def add_to_db(abbreviation: str, website: str, link: str) -> None:
    config_ = load_settings()
    if abbreviation in config_:
        if config_[abbreviation]["desired"] is True:
            logger.info(f"{abbreviation} already loaded.")
        else:
            config_[abbreviation]["desired"] = True
    config_[abbreviation] = {
        "desired": True,
        "file": None,
        "link": link,
        "website": website,
        "loaded": False,
    }
    save_settings(config_)
    load_from_config()


def delete_from_db(abbreviation: str) -> None:
    delete_from_chroma(law_code=abbreviation)
    config_ = load_settings()
    del config_[abbreviation]
    save_settings(config_)


def describe_loaded() -> str:
    config = load_settings()
    description_ = "<br>".join([law + ": " + config[law]["website"] for law in config])
    return description_


with gr.Blocks() as demo:

    gr.Markdown("# German law bot")
    gr.Markdown("## Information and settings")

    show_latest = gr.Button("Update and show loaded codes of law")
    description = gr.Markdown()
    show_latest.click(fn=describe_loaded, outputs=description)

    law_filter_ = gr.Dropdown(
        label="Optionally limit the search to specific laws.",
        choices=[law for law in load_settings()],
        multiselect=True,
    )
    n_results_ = gr.Number(
        value=5, label="Number of chunks to be considered", precision=0, render=False
    )

    gr.ChatInterface(
        echo,
        additional_inputs=[
            n_results_,
            law_filter_,
        ],
    )

    gr.Markdown("## Load additional codes of laws")
    with gr.Row():
        abbreviation = gr.Textbox(label="Abbreviation of the law", placeholder="E.g., BGB")
        website = gr.Textbox(
            label="Link to the online resource",
            placeholder="E.g., https://www.gesetze-im-internet.de/bgb/"
        )
        link = gr.Textbox(
            label="Link to the XML download",
            placeholder="E.g., https://www.gesetze-im-internet.de/bgb/xml.zip"
        )
        load_btn = gr.Button("Load")
        load_btn.click(add_to_db, inputs=[abbreviation, website, link])
    gr.Markdown("## Delete codes of laws")
    with gr.Row():
        abbreviation = gr.Textbox(label="Abbreviation of the law", placeholder="E.g., BGB")
        load_btn = gr.Button("Delete")
        load_btn.click(delete_from_db, inputs=[abbreviation])


if __name__ == "__main__":
    demo.queue().launch(share=False)
