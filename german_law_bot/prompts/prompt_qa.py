#!/usr/bin/env python3

PROMPT_RAG = """\
Beantworte die folgende Frage nur basierend auf dem bereitgestellten Kontext.
Solltest du die Frage nicht rein basierend auf dem Kontext beantworten können, antworte, dass du die Antwort nicht weißt.
KONTEXT:
<context>
FRAGE:
<question>
"""

PROMPT_MAP_REDUCE = """\
Beantworte die folgende Frage nur basierend auf dem bereitgestellten Kontext.
Begründe deine Antwort mit einem knappen Satz.
Sollte der Kontext ungeeignet sein um die Frage zu beantworten, antworte NUR mit dem einen Wort `irrelevant`.
KONTEXT:
<context>
Frage:
<question>
"""

PROMPT_MAP_REDUCE_SUMMARY = """\
Beantworte die folgende Frage nur basierend auf dem bereitgestellten Informationen, welche basierend auf anderen Ausschnitten gewonnen wurden.
Solltest du die Frage nicht rein basierend auf dem Kontext beantworten können, antworte, dass du die Antwort nicht weißt.
KONTEXT:
<context>
FRAGE:
<question>
"""
