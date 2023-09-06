#!/usr/bin/env python3

PROMPT_RAG = """\
Beantworte die folgende Frage nur basierend auf dem bereitgestellten Kontext.
Begründe deine Antwort mit einem knappen Satz.
Falls es relevante Randbedingungen gibt, beschreibe diese in einem weiteren Satz.
Solltest du die Frage nicht rein basierend auf dem Kontext beantworten können, \
antworte, dass du die Antwort nicht weißt.
KONTEXT:
{context}
FRAGE:
{question}
"""

PROMPT_MAP_REDUCE = """\
Beantworte die folgende Frage nur basierend auf dem bereitgestellten Kontext.
Begründe deine Antwort mit einem knappen Satz.
Beschreibe in einem weiteren Satz die Voraussetzungen für die Anwendbarkeit dieses Gesetzes.
Sollte der Kontext ungeeignet sein um die Frage zu beantworten, \
antworte NUR mit dem einen Wort `irrelevant`.
KONTEXT:
{context}
Frage:
{question}
"""

PROMPT_MAP_REDUCE_SUMMARY = """\
Beantworte die folgende Frage nur basierend auf dem folgenden Kontext, \
welcher aus den gegebenen Ausschnitten zusammengefasst wurde.
Begründe deine Antwort mit einem knappen Satz.
Beschreibe in einem weiteren Satz die Voraussetzungen für die Anwendbarkeit der \
relevanten Gesetzes.
Sollte die Frage nicht rein basierend auf dem Kontext beantwortbar sein, \
antworte, dass du die Antwort nicht weißt.
Sollte der Kontext widersprüchliche Informationen enthalten, \
beschreibe diesen Widerspruch knapp.
KONTEXT:
{context}
FRAGE:
{question}
"""

PROMPT_SB_GEN_QUESTION = """\
Nimm die Rolle eines freundlichen und hilfreichen Lernpartners ein.
Erstelle hierfür basierend auf dem im Folgenden gegebenen Kontext eine Frage.
Diese Frage soll geeignet sein, um yu prüfen, ob der Partner das Gesetz kennt \
und verstanden hat.
Antworte NUR mit der generierten Frage.
KONTEXT:
{context}
"""

PROMPT_SB_ASSESS_ANSWER = """\
Nimm die Rolle eines freundlichen und hilfreichen Lernpartners ein.
Ein Lernender sollte die später genannte Frage beantworten.
Beurteile basierend auf dem gegebenen Kontext, \
ob der Lösungsvorschlag des Lernenden korrekt ist.
Falls der Lösungsvorschlag falsch ist, gib eine knappe und präzise \
Erklärung der richtigen Antwort.
Antworte NUR mit der Bewertung des Lösungsvorschlags und einer Erklärung.
FRAGE:
{question}
KONTEXT:
{context}
LÖSUNGSVORSCHLAG DES LERNENDEN:
{response}
"""
