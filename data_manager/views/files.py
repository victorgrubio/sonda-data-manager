'''
Created on 18 mar. 2020

@author: victor
'''
from datetime import datetime
import traceback
import json
from flask import Blueprint, abort

from helper import global_variables as gv
from helper import config as cfg
from helper import utils

files = Blueprint('files', __name__, url_prefix="/videoAnalysis/files")

@files.route('/<filename>', methods=['GET'])
def api_get_file_by_filename(filename):
    """
    Get file from a provided filename
    ---
    get:
        tags: 
            - files
        summary: Gets a file by its URL
        description: Returns the file correspondent to the specified URL
        operationId: get_file_by_filename
        parameters: 
            - name: api_key
              in: header
              required: false
              schema:
                type: string
            - name: filename
              in: path
              required: true
              schema:
                type: string
        responses: 
            200:
                description: File requested
                content:
                    application/json:
                        schema:
                            type: file
            404: 
                description: File not found
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
        response = gv.api_dm.file_router.get_file_by_filename(filename)
        gv.logger.info("File generated successfully")
        response.headers.set('Content-Disposition', 'attachment', filename=filename)
    except FileNotFoundError:
        abort(status=404, description=f"File {filename} not found on server")
    except Exception as e:
        gv.logger.error(e)
        output = utils.build_output(task=cfg.get_file_by_filename, status=500,
                                        message=str(e), output={})
        response = json.dumps(output)
    return response, status
