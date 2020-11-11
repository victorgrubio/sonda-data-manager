#!/bin/bash
SOURCE_CODE_PATH=data_manager/
DATA_MANAGER_PACKAGE_PATH=$(pwd)/$SOURCE_CODE_PATH

export API_PORT=5001
export WEB_PORT=3000
export DB_PORT=27020
export PYTHONPATH="${PYTHONPATH}:$DATA_MANAGER_PACKAGE_PATH"
if [ -d "venv" ]; then
    . venv/bin/activate
else
    python3 -m venv venv
    pip install -r requirements.txt
    pip install sphinx sphinx_rtd_theme
fi
cd docs/ && make clean && cd ..
rm -Rf docs/source/docstring/*
sphinx-apidoc -e -f -o docs/source/docstring/ $SOURCE_CODE_PATH
cd docs/ && make html && cd ..
