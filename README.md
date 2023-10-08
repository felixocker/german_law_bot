# :judge: german_law_bot
A QA bot and a study buddy for German law. \
Disclaimer: This bot does not, and is not intended to, constitute legal advice. \
To get good results, be as precise as possible with your prompts.


## Ideas
* :speech_balloon: Basic QA for German laws
* :student:	Study buddy for learning about German laws
* :telescope: A bot for coming up with legal arguments for specific cases based on German laws :construction:


## Demo

### QA Bot
<img src="https://github.com/felixocker/german_law_bot/raw/main/docs/qa-bot.gif" alt="QA bot" width="800"/>

### Study buddy
<img src="https://github.com/felixocker/german_law_bot/raw/main/docs/studybuddy.gif" alt="Study buddy" width="800"/>


## Instructions
* Set an environment variable for your `OPENAI_API_KEY`, see [these instructions](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety)
* Install dependencies
  * With poetry (recommended): `poetry install`
  * With pip: `python -m venv .venv && source .venv/bin/activate && pip install .`
* Browser interface
  * If installed with poetry: `cd german_law_bot && poetry run python frontend.py`
  * If installed with pip: `cd german_law_bot && python frontend.py`
* (Limited) command line usage:
  * Specify the codes of law you want to load in `config.yaml` (provide the download links for the XML zips, see the example for the BGB below)
  * Load the data: `python ingest.py`
  * Run QA bot: `python qa.py`

```yaml
BGB:
  desired: true
  file: BJNR001950896.xml
  link: https://www.gesetze-im-internet.de/bgb/xml.zip
  loaded: true
  website: https://www.gesetze-im-internet.de/bgb/
```


## Contents
* `data/`
  * `chroma/` - the persistent vector store lives here
  * `downloads/` - source files are stored here
* `docs/` - demo gifs
* `german_law_bot/`
  * `prompts/`
    * `prompt_qa.py` - contains all prompts used
  * `config.yaml` - settings for what to load
  * `constants.py` - some generic settings
  * `frontend.py` - gradio-based frontend
  * `history.py` - keep track of interactions with the bot
  * `ingest.py` - download codes of law, extract data, feed into vector store
  * `qa.py` - QA using RAG
  * `utils.py` - utilities that are reused across modules


## Dev notes
* Package management: poetry
* Linting: ruff
* Formatting: black
