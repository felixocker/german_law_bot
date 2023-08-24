# german_law_bot :judge:
A bot for QA over German law.


## Contents
* german_law_bot
  * `constants.py` - some generic settings
  * `ingest.py` - download law file, extract data, feed into vector store
  * `qa.py` - QA using RAG
  * `frontend.py` - WIP
* data
  * chroma - the persistent vector store lives here
  * sources - source files are stored here


## Ideas
* :grey_question::grey_exclamation: Basic QA for German laws
* :telescope: A bot for coming up with legal arguments for specific cases based on German laws


## Sources
* [EStG](https://www.gesetze-im-internet.de/estg/)


## Dev notes
* Package management: poetry
* Linting: ruff
* Formatting: black
