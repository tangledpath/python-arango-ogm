#!/bin/bash
source ${BASH_SOURCE%/*}/clean.sh
poetry run pdoc python_arango_ogm -o ./docs
poetry build
