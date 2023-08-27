#!/usr/bin/env python3
"""Gradio frontend"""
import gradio as gr

from qa import rag_query


with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    clear = gr.ClearButton([msg, chatbot])

    def respond(message: str, chat_history):
        rag_response = rag_query(query=message, n_results=5)
        chat_history.append((message, rag_response))
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])

demo.launch()
