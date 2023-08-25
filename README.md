# :judge: german_law_bot
A bot for QA over German law.


## Contents
* german_law_bot
  * `constants.py` - some generic settings
  * `ingest.py` - download law file, extract data, feed into vector store
  * `qa.py` - QA using RAG
  * `frontend.py` - WIP :construction:
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
FRAGE: _Wer trägt im Widerrufsfall die Gefahr der Rücksendung der Waren?_ \
ANTWORT: _Im Widerrufsfall trägt der Käufer bzw. Verbraucher die Gefahr der Rücksendung der Waren. Quelle: BGB_447, BGB_357d (Auch geprueft: BGB_644)_

## Sources
* [EStG](https://www.gesetze-im-internet.de/estg/)
* [BGB](https://www.gesetze-im-internet.de/bgb/index.html)


## Dev notes
* Package management: poetry
* Linting: ruff
* Formatting: black
