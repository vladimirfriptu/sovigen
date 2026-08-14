python := "python3"

# install dev deps into .venv
setup:
    {{python}} -m venv .venv
    .venv/bin/pip install -r requirements-dev.txt

# run the test suite
test:
    .venv/bin/python -m pytest

# create a new song folder: just new "My Track Name" [--source ... --series ... --language ...]
new title *args:
    {{python}} -m sovigen.cli new "{{title}}" {{args}}

# advance a song to the next stage: just advance my-track-name
advance slug:
    {{python}} -m sovigen.cli advance "{{slug}}"

# place a downloaded file into the song folder: just import my-track ~/Downloads/take.mp3
import slug path:
    {{python}} -m sovigen.cli import "{{slug}}" "{{path}}"

# build one song by slug: just build my-track-name [--viz]
build slug *args:
    {{python}} -m sovigen.cli build "{{slug}}" {{args}}

# build every song at stage 'ready'
build-all:
    {{python}} -m sovigen.cli build-all

# mark a song published: just publish my-track-name
publish slug:
    {{python}} -m sovigen.cli publish "{{slug}}"

# show all songs and their stages: just status [--json]
status *args:
    {{python}} -m sovigen.cli status {{args}}
