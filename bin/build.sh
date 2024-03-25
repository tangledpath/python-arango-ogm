#!/bin/bash
source ${BASH_SOURCE%/*}/clean.sh
# Run in browser:
#poetry run pdoc python_arango_ogm/* --logo https://github.com/tangledpath/python-arango-ogm/blob/master/pao.png --favicon https://github.com/tangledpath/python-arango-ogm/blob/master/pao_sm.png
poetry run pdoc python_arango_ogm/* -o ./docs --logo https://github.com/tangledpath/python-arango-ogm/blob/master/pao.png?raw=true --favicon https://github.com/tangledpath/python-arango-ogm/blob/master/pao_sm.png?raw=true
poetry build
