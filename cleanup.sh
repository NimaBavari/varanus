#!/usr/bin/env bash
pip3 install -r dev_requirements.txt
isort -rc .
autoflake -r --in-place --remove-unused-variables .
black -l 120 .
flake8 --max-line-length 120 . --exclude .venv
mypy --disable-error-code import-not-found --disable-error-code import-untyped --explicit-package-bases .
rm -rf .mypy_cache