#!/bin/bash
find . -name __pycache__ | xargs rm -rf
find . -name .ipynb_checkpoints | xargs rm -rf
rm -rf dist
rm -rf docs
rm -rf .pytest_cache
rm -rf .ruff_cache
