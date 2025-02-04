.PHONY: install run lint test

install:
\tpoetry install

run:
\tpoetry run python -m my_audio_app.main

lint:
\tpoetry run flake8 my_audio_app

test:
\tpoetry run pytest -v
