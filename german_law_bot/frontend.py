#!/usr/bin/env python3
"""Gradio frontend"""
import logging
import time

import gradio as gr
import pandas as pd

from constants import (
    AUTO_LAUNCH_BROWSER,
    BASE_CHAT_MODEL,
    CHAT_MODELS,
)
from history import retrieve
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


MODEL = BASE_CHAT_MODEL
SB_CONTEXT: str = ""
SB_QUESTION: str = ""


def set_model(model_) -> None:
    global MODEL
    MODEL = model_
    logger.info(f"Set model to {model_}")


def echo(message, history, n_results, law_filter):
    global MODEL
    response = rag_query(
        query=message, n_results=n_results, law_filter=law_filter, model=MODEL
    )
    for i, _ in enumerate(response):
        time.sleep(0.02)
        yield response[: i + 1]


def gen_question_sb(context, n_results, law_filter):
    logger.info(f"Generating question for context {context}")
    global MODEL, SB_CONTEXT, SB_QUESTION
    background, response = generate_question(
        context=context, n_results=n_results, law_filter=law_filter, model=MODEL
    )
    SB_CONTEXT, SB_QUESTION = background, response
    return response


def rate_response_sb(topic, response):
    global MODEL, SB_CONTEXT, SB_QUESTION
    response = assess_answer(
        topic=topic,
        question=SB_QUESTION,
        background=SB_CONTEXT,
        response=response,
        model=MODEL,
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


def retrieve_history(hist_filter: str) -> dict:
    objs = retrieve(hist_filter)
    df = pd.DataFrame([o.__dict__ for o in objs])
    return gr.Dataframe.update(value=df)


with gr.Blocks() as demo:
    gr.Markdown("# 🧑‍⚖🧞 German law bot")

    with gr.Tab("Einstellungen"):
        gr.Markdown("## Informationen und Einstellungen")

        description = gr.Markdown(describe_loaded())

        with gr.Row():
            set_model_radio = gr.Radio(
                label=(
                    "Wähle ein Sprachmodell. "
                    "gpt-4 funktioniert am besten, ist aber langsamer und teurer"
                ),
                choices=list(CHAT_MODELS),
                value=BASE_CHAT_MODEL,
            )

        gr.Markdown("## Lade weitere Gesetze")
        with gr.Row():
            abbreviation_add = gr.Textbox(
                label="Abkürzung des Gesetzes", placeholder="Z.B. BGB"
            )
            website = gr.Textbox(
                label="Link zur Onlinequelle",
                placeholder="Z.B. https://www.gesetze-im-internet.de/bgb/",
            )
            link = gr.Textbox(
                label="Link zum XML Download",
                placeholder="Z.B. https://www.gesetze-im-internet.de/bgb/xml.zip",
            )
            status_add = gr.Textbox(label="Status", placeholder="Bereit")
        with gr.Row():
            load_btn = gr.Button("Laden")
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
        gr.Markdown("## Lösche Gesetze")
        with gr.Row():
            abbreviation_del = gr.Dropdown(
                label="Abkürzung des zu löschenden Gesetzes",
                choices=[law for law in load_settings()],
                multiselect=False,
            )
            status_del = gr.Textbox(label="Status", placeholder="Bereit")
        with gr.Row():
            del_btn = gr.Button("Löschen")

    with gr.Tab("QA Bot"):
        gr.Markdown("## QA Bot für deutsche Gesetze")

        law_filter_ = gr.Dropdown(
            label="Schränke die Suche auf bestimmte Gesetze ein (optional)",
            choices=[law for law in load_settings()],
            multiselect=True,
        )

        n_results_ = gr.Number(
            value=5,
            label="Anzahl der zu berücksichtigenden Textabschnitte",
            precision=0,
            render=False,
        )

        gr.ChatInterface(
            echo,
            submit_btn="Fragen",
            stop_btn="Abbrechen",
            retry_btn="🔄 Erneut versuchen",
            undo_btn="↩️ Zurücksetzen",
            clear_btn="🗑️ Löschen",
            additional_inputs_accordion_name="Weitere Einstellungen",
            additional_inputs=[
                n_results_,
                law_filter_,
            ],
        )

    with gr.Tab("Study buddy"):
        gr.Markdown("## Study buddy um deutsche Gesetze zu lernen")

        law_filter_sb = gr.Dropdown(
            label="Wähle Gesetze für die Fragen generiert werden",
            choices=[law for law in load_settings()],
            multiselect=True,
        )

        content_sb = gr.Textbox(
            label="Relevanter Bereich",
            placeholder="Z.B. Widerruf",
        )

        n_results_sb = gr.Number(
            value=5,
            label=(
                "Anzahl an Gesetzen, aus denen Fragen generiert werden "
                "(erhöht die Variation)"
            ),
            precision=0,
        )

        with gr.Row():
            generate_btn_sb = gr.Button("Generiere eine Frage")

        with gr.Row():
            question_sb = gr.Textbox(
                label="Frage",
                placeholder="Zu generieren...",
            )

        with gr.Row():
            show_hint_btn_sb = gr.Button("Gib mir einen Tipp")
            hide_hint_btn_sb = gr.Button("Verstecke den Tipp")
        hint_sb = gr.Textbox("", label="Hint", visible=False)

        with gr.Row():
            input_sb = gr.Textbox(
                label="Antwort",
            )

        with gr.Row():
            submit_btn_sb = gr.Button("Bestätigen")

        with gr.Row():
            solution_sb = gr.Textbox(
                label="Lösung",
                placeholder="Zu generieren...",
            )

        with gr.Row():
            gr.ClearButton(
                components=[content_sb, question_sb, input_sb, solution_sb],
                value="🗑️ Löschen",
            )

    with gr.Tab("Historie"):
        gr.Markdown("## Durchsuche bisherige Interaktionen mit dem Bot")

        with gr.Row():
            history_filter_radio = gr.Radio(
                label="Wähle den Interaktionstyp, den du durchsuchen möchtest.",
                choices=["qabot", "studybuddy"],
                value="qabot",
            )
            refresh_hist_btn = gr.Button("Aktualisieren")

        with gr.Row():
            history_df = gr.Dataframe(interactive=False, wrap=True)

    set_model_radio.change(
        fn=set_model,
        inputs=[set_model_radio],
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
    show_hint_btn_sb.click(
        fn=lambda value: gr.Textbox.update(value=SB_CONTEXT, visible=True),
        outputs=[hint_sb],
    )
    hide_hint_btn_sb.click(
        fn=lambda value: gr.Textbox.update(value="", visible=False),
        outputs=[hint_sb],
    )
    submit_btn_sb.click(
        fn=rate_response_sb,
        inputs=[content_sb, input_sb],
        outputs=[solution_sb],
    )
    history_filter_radio.change(
        fn=retrieve_history,
        inputs=[history_filter_radio],
        outputs=[history_df],
    )
    refresh_hist_btn.click(
        fn=retrieve_history,
        inputs=[history_filter_radio],
        outputs=[history_df],
    )


if __name__ == "__main__":
    demo.queue().launch(share=False, inbrowser=AUTO_LAUNCH_BROWSER)
