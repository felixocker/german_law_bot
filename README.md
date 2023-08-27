# :judge: german_law_bot
A bot for QA over German law. \
Disclaimer: This bot does not, and is not intended to, constitute legal advice. \
To get good results, be as precise as possible with your prompts.


## Contents
* german_law_bot
  * `constants.py` - some generic settings
  * `ingest.py` - download law file, extract data, feed into vector store
  * `qa.py` - QA using RAG
  * `frontend.py` - WIP :construction:
  * `config.yaml` - settings for what to load
* data
  * `chroma/` - the persistent vector store lives here
  * `downloads/` - source files are stored here


## Ideas
* :speech_balloon: Basic QA for German laws
* :telescope: A bot for coming up with legal arguments for specific cases based on German laws :construction:


## Examples

### EStG
FRAGE: _Gilt die Überführung eines Wirtschaftsguts in das Privatvermögen des Steuerpflichtigen durch Entnahme als Anschaffung?_ \
ANTWORT: _Ja, die Überführung eines Wirtschaftsguts in das Privatvermögen des Steuerpflichtigen durch Entnahme gilt als Anschaffung. Quelle: EStG_23_

### BGB
FRAGE: _Wer trägt im Widerrufsfall bei einem Verbrauchervertrag die Gefahr der Rücksendung der Waren?_ \
ANTWORT: _Der Verbraucher trägt bei Widerruf bei einem Verbrauchervertrag die Gefahr der Rücksendung der Waren. Quelle: BGB_355, BGB_357d (Auch geprueft: BGB_357e)_

## Sources
* [EStG](https://www.gesetze-im-internet.de/estg/)
* [BGB](https://www.gesetze-im-internet.de/bgb/)


## Dev notes
* Package management: poetry
* Linting: ruff
* Formatting: black
