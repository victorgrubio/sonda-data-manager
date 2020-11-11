#!/bin/bash
SOURCE_CODE_PATH=data_manager/
DATA_MANAGER_PACKAGE_PATH=$(pwd)/$SOURCE_CODE_PATH

export API_PORT=5001
export WEB_PORT=3000
export DB_PORT=27017
export PYTHONPATH="${PYTHONPATH}:$DATA_MANAGER_PACKAGE_PATH"
if [ -d "venv" ]; then
    . venv/bin/activate
    pip install -r requirements.txt
else
    echo "NO VENV"
    python3 -m venv venv
    . venv/bin/activate 
    pip install -r requirements.txt
fi
python3 data_manager/swagger.py
