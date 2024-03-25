#!/bin/bash
source ${BASH_SOURCE%/*}/clean.sh
# Run in browser:
#poetry run pdoc python_arango_ogm --logo https://raw.githubusercontent.com/tangledpath/python-arango-ogm/master/pao.png --favicon https://raw.githubusercontent.com/tangledpath/python-arango-ogm/master/pao_sm.png
poetry run pdoc python_arango_ogm -o ./docs --logo https://raw.githubusercontent.com/tangledpath/python-arango-ogm/master/pao.png --favicon https://raw.githubusercontent.com/tangledpath/python-arango-ogm/master/pao_sm.png
poetry build
