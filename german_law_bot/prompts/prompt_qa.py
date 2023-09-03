#!/usr/bin/env python3

PROMPT_RAG = """\
Beantworte die folgende Frage nur basierend auf dem bereitgestellten Kontext.
Begründe deine Antwort mit einem knappen Satz.
Falls es relevante Randbedingungen gibt, beschreibe diese in einem weiteren Satz.
Solltest du die Frage nicht rein basierend auf dem Kontext beantworten können, antworte, dass du die Antwort nicht weißt.
KONTEXT:
<context>
FRAGE:
<question>
"""

PROMPT_MAP_REDUCE = """\
Beantworte die folgende Frage nur basierend auf dem bereitgestellten Kontext.
Begründe deine Antwort mit einem knappen Satz.
Falls es relevante Randbedingungen gibt, beschreibe diese in einem weiteren Satz.
Sollte der Kontext ungeeignet sein um die Frage zu beantworten, antworte NUR mit dem einen Wort `irrelevant`.
KONTEXT:
<context>
Frage:
<question>
"""

PROMPT_MAP_REDUCE_SUMMARY = """\
Beantworte die folgende Frage nur basierend auf dem folgenden Kontext, welcher aus den gegebenen Ausschnitten zusammengefasst wurde.
Begründe deine Antwort mit einem knappen Satz.
Falls es relevante Randbedingungen gibt, beschreibe diese in einem weiteren Satz.
Solltest du die Frage nicht rein basierend auf dem Kontext beantworten können, antworte, dass du die Antwort nicht weißt.
KONTEXT:
<context>
FRAGE:
<question>
"""
