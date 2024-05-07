#!/bin/bash
find fast_api_jwt -name "*.py" | xargs  autopep8 --in-place