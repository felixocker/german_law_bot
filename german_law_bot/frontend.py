#!/usr/bin/env python3
"""Gradio frontend"""
import time
import yaml

import gradio as gr

from qa import rag_query
from constants import CONFIG


with open(CONFIG, "r") as f:
    config = yaml.safe_load(f)


def echo(message, history, n_results, law_filter):
    response = rag_query(query=message, n_results=n_results, law_filter=law_filter)
    for i, _ in enumerate(response):
        time.sleep(0.02)
        yield response[: i + 1]


with gr.Blocks() as demo:
    gr.Markdown("# German law bot")
    gr.Markdown("<br>".join([law + ": " + config[law]["website"] for law in config]))
    law_filter_ = gr.Dropdown(
        label="Optionally limit the search to specific laws.",
        choices=[law for law in config],
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


if __name__ == "__main__":
    demo.queue().launch()
