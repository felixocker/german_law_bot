#!/usr/bin/env python3
"""Gradio frontend"""
import logging
import time

import gradio as gr

from ingest import (
    load_from_config,
    delete_from_chroma,
    get_chroma_stats,
)
from qa import (
    rag_query,
    generate_question,
    assess_answer,
)
from utils import (
    load_settings,
    save_settings,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


SB_CONTEXT: str = ""
SB_QUESTION: str = ""


def echo(message, n_results, law_filter):
    response = rag_query(query=message, n_results=n_results, law_filter=law_filter)
    for i, _ in enumerate(response):
        time.sleep(0.02)
        yield response[: i + 1]


def gen_question_sb(context, n_results, law_filter):
    logger.info(f"Generating question for context {context}")
    background, response = generate_question(
        context=context, n_results=n_results, law_filter=law_filter
    )
    global SB_CONTEXT
    SB_CONTEXT = background
    global SB_QUESTION
    SB_QUESTION = response
    return response


def rate_response_sb(response):
    global SB_CONTEXT
    global SB_QUESTION
    response = assess_answer(
        question=SB_QUESTION, background=SB_CONTEXT, response=response
    )
    response += "\n\nQUELLE:\n\n" + SB_CONTEXT
    return response


def add_to_db(
    abbreviation: str, website: str, link: str
) -> tuple[None, dict, dict, dict, str]:
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
    return (
        None,
        gr.Dropdown.update(choices=[law for law in load_settings()]),
        gr.Dropdown.update(choices=[law for law in load_settings()]),
        gr.Dropdown.update(choices=[law for law in load_settings()]),
        describe_loaded(),
    )


def delete_from_db(abbreviation: str) -> tuple[None, dict, dict, dict, str]:
    delete_from_chroma(law_code=abbreviation)
    config_ = load_settings()
    del config_[abbreviation]
    save_settings(config_)
    return (
        None,
        gr.Dropdown.update(choices=[law for law in load_settings()]),
        gr.Dropdown.update(choices=[law for law in load_settings()]),
        gr.Dropdown.update(choices=[law for law in load_settings()]),
        describe_loaded(),
    )


def describe_loaded() -> str:
    config = load_settings()
    description_ = "<br>".join([law + ": " + config[law]["website"] for law in config])
    description_ += "<br>" + get_chroma_stats()
    return description_


with gr.Blocks() as demo:
    gr.Markdown("# German law bot")

    with gr.Tab("Settings"):
        gr.Markdown("## Information and settings")

        description = gr.Markdown(describe_loaded())

        gr.Markdown("## Load additional codes of laws")
        with gr.Row():
            abbreviation_add = gr.Textbox(
                label="Abbreviation of the law", placeholder="E.g., BGB"
            )
            website = gr.Textbox(
                label="Link to the online resource",
                placeholder="E.g., https://www.gesetze-im-internet.de/bgb/",
            )
            link = gr.Textbox(
                label="Link to the XML download",
                placeholder="E.g., https://www.gesetze-im-internet.de/bgb/xml.zip",
            )
            status_add = gr.Textbox(label="Status", placeholder="Idle")
        with gr.Row():
            load_btn = gr.Button("Load")
        gr.Examples(
            examples=[
                [
                    "BGB",
                    "https://www.gesetze-im-internet.de/bgb/",
                    "https://www.gesetze-im-internet.de/bgb/xml.zip",
                ],
                [
                    "EStG",
                    "https://www.gesetze-im-internet.de/estg/",
                    "https://www.gesetze-im-internet.de/estg/xml.zip",
                ],
            ],
            inputs=[abbreviation_add, website, link],
            outputs=status_add,
            fn=add_to_db,
            cache_examples=False,
        )
        gr.Markdown("## Delete codes of laws")
        with gr.Row():
            abbreviation_del = gr.Dropdown(
                label="Abbreviation of the law to be deleted",
                choices=[law for law in load_settings()],
                multiselect=False,
            )
            status_del = gr.Textbox(label="Status", placeholder="Idle")
        with gr.Row():
            del_btn = gr.Button("Delete")

    with gr.Tab("QA bot"):
        gr.Markdown("## QA bot for German laws")

        law_filter_ = gr.Dropdown(
            label="Optionally limit the search to specific laws",
            choices=[law for law in load_settings()],
            multiselect=True,
        )

        n_results_ = gr.Number(
            value=5,
            label="Number of chunks to be considered",
            precision=0,
            render=False,
        )

        gr.ChatInterface(
            echo,
            additional_inputs=[
                n_results_,
                law_filter_,
            ],
        )

    with gr.Tab("Study buddy"):
        gr.Markdown("## Study buddy for learning about German laws")

        law_filter_sb = gr.Dropdown(
            label="Choose laws for the question generation",
            choices=[law for law in load_settings()],
            multiselect=True,
        )

        content_sb = gr.Textbox(
            label="Content of interest",
            placeholder="E.g., Widerruf",
        )

        n_results_sb = gr.Number(
            value=5, label="Number of chunks to generate question from", precision=0
        )

        with gr.Row():
            generate_btn_sb = gr.Button("Generate question")

        with gr.Row():
            question_sb = gr.Textbox(
                label="Question",
                placeholder="To be generated...",
            )

        with gr.Row():
            input_sb = gr.Textbox(
                label="Your answer",
            )

        with gr.Row():
            submit_btn_sb = gr.Button("Submit")

        with gr.Row():
            solution_sb = gr.Textbox(
                label="Solution",
                placeholder="To be generated...",
            )

    load_btn.click(
        fn=add_to_db,
        inputs=[abbreviation_add, website, link],
        outputs=[status_add, law_filter_, law_filter_sb, abbreviation_del, description],
    )
    del_btn.click(
        fn=delete_from_db,
        inputs=[abbreviation_del],
        outputs=[status_del, law_filter_, law_filter_sb, abbreviation_del, description],
    )
    generate_btn_sb.click(
        fn=gen_question_sb,
        inputs=[content_sb, n_results_sb, law_filter_sb],
        outputs=[question_sb],
    )
    submit_btn_sb.click(
        fn=rate_response_sb,
        inputs=[input_sb],
        outputs=[solution_sb],
    )


if __name__ == "__main__":
    demo.queue().launch(share=False)
