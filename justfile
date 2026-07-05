python := "python3"

# install dev deps into .venv
setup:
    {{python}} -m venv .venv
    .venv/bin/pip install -r requirements-dev.txt

# run the test suite
test:
    .venv/bin/python -m pytest

# create a new song folder: just new "My Track Name"
new title:
    {{python}} -m sovigen.cli new "{{title}}"

# mark a song ready to build: just ready my-track-name
ready slug:
    {{python}} -m sovigen.cli ready "{{slug}}"

# build one song by slug: just build my-track-name
build slug:
    {{python}} -m sovigen.cli build "{{slug}}"

# build every song at stage 'ready'
build-all:
    {{python}} -m sovigen.cli build-all

# mark a song published: just publish my-track-name
publish slug:
    {{python}} -m sovigen.cli publish "{{slug}}"

# show all songs and their stages
status:
    {{python}} -m sovigen.cli status
