# german_law_bot
A bot for QA over German law.


## Contents
* german_law_bot
  * `constants.py` - some generic settings
  * `ingest.py` - download law file, extract data, feed into vector store
  * `qa.py` - question answering over vector store
  * `frontend.py` - WIP
* data
  * chroma - the persistent vector store lives here
  * sources - source files are stored here


## Sources
* [EStG](https://www.gesetze-im-internet.de/estg/)


## Dev notes
* Package management: poetry
* Linting: ruff
* Formatting: black
