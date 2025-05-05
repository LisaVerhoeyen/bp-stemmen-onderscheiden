# bp-stemmen-onderscheiden

## Install dependencies

### Pyannote
* `pip install pyannote.audio`
* `pip install pydub`
* `pip install pyannote.database`

### Simple-diarizer (only used in model testing)
* `pip install simple-diarizer`
* `pip install speechbrain`

### Extract audio from video
* `pip install audio_extract`

## Nodig in .env

* huggingface token

## Andere opmerkingen

De paden in de [config file](./pyannote/pipeline/config.yaml) voor de pipeline zijn hardgecodeerd naar een pad op mijn pc, pas deze aan voor gebruik