'''
Created on 18 mar. 2020

@author: victor
'''
import traceback
import json
from flask import Blueprint, abort, request

from helper import global_variables as gv
from helper import config as cfg
from helper import utils

db = Blueprint('db', __name__, url_prefix="/videoAnalysis/db")

@db.route('/export', methods=['GET'])
def api_export_db():
    """
    Export DB to GZIP
    ---
    get:
        tags: 
            - database
        summary: Export DB to GZIP
        description: Export complete DB to GZIP file
        operationId: export_db
        parameters: 
            - name: api_key
              in: header
              required: false
              schema:
                type: string
        responses: 
            200:
                description: DB as GZIP
                content:
                    application/json:
                        schema:
                            type: file
            404: 
                description: Empty DB
                content:
                    application/json:
                        schema: ErrorResponse
            default:
                description: Unexpected server response
                content:
                    application/json: 
                        schema: ErrorResponse
        security: 
            -  api_key: 
    """
    status = 200
    try:
        response = gv.api_dm.db_router.export_db()
    except Exception as e:
        gv.logger.error(e)
        gv.logger.error(traceback.print_exc())
        status=500
        output = utils.build_output(task=cfg.export_db_task, status=500,
                                        message=str(e), output={})
        response = json.dumps(output)
    return response, status


@db.route('/import', methods=['POST'])
def api_import_db():
    """
    Imports DB from GZIP
    ---
    post:
        tags: 
            -  database
        summary: Imports DB from GZIP
        description: Imports DB from GZIP
        operationId: import_db
        parameters: 
            -   name: api_key
                in: header
                required: false
                schema:
                    type: string
            -   name: file
                in: formData
                description: DB in GZIP file with valid schema
                required: true
                schema:
                    type: file
        responses: 
            200:
                description: DB imported successfully
                content:
                    application/json:
                        schema: ApiResponse
            405: 
                description: Invalid input
                content:
                    application/json:
                        schema: ErrorResponse
            default:
                description: Unexpected server response
                content:
                    application/json: 
                        schema: ErrorResponse
        security: 
            -  api_key: 
    """
    status = 200
    try:
        # check if the post request has the file part
        if 'file' not in request.files:
            raise Exception("No file has been sent to the API")
        output = gv.api_dm.db_router.import_db(request)
        response = json.dumps(output)
    except Exception as e:
        gv.logger.error(e)
        status=500
        output = utils.build_output(task=cfg.import_db_task, status=500,
                                        message=str(e), output={})
        response = json.dumps(output)
    return response, status