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


documents = Blueprint('documents', __name__, url_prefix="/videoAnalysis/documents")

@documents.route('/bulk', methods=['POST'])
def api_post_bulk_document():
    """
    Bulk documents into database
    ---
    post: 
        tags: 
            - documents
        summary: Add a new document to the database
        description: Add new document from probe to MongoDB
        operationId: bulk_document
        parameters: 
            - name: api_key
              in: header
              required: false
              schema:
                type: string
            - name: mode
              in: header
              description: Working mode
              required: true
              schema:
                type: string
        requestBody:
            description: Document from probe
            required: true
            content:
                application/json:
                    schema: VideoAnalysisSchema
        responses: 
            200:
                description: successful operation
                content:
                    application/json:
                        schema: ApiResponse
            405: 
                description: Invalid input
                schema: ErrorResponse
            default:
                description: Unexpected server response
                content:
                    application/json: 
                        schema: ErrorResponse
        security: 
            -   api_key: 
    """
    status = 200
    try:
        input_document = json.dumps(request.get_json(force=True))
        headers = request.headers
        output = gv.api_dm.document_router.bulk_document_to_db(
            input_document=input_document,
            headers=headers)
        response = json.dumps(output)
    except Exception as e:
        gv.logger.error(e)
        gv.logger.error(traceback.print_exc())
        status=500
        output = utils.build_output(task=cfg.bulk_data_task, status=500,
                                        message=str(e), output={})
        response = json.dumps(output)
    return response, status


@documents.route('/last', methods=['GET'])
def api_get_last_document():
    """
    Gets last measure from probe
    ---
    get:
        tags: 
            -  documents
        summary:  Gets last measure
        description:  Gets last measure from DB
        operationId: get_last_document
        parameters: 
            - name: api_key
              in: header
              required: false
              schema:
                type: string
        responses: 
            200:
                description: Last document in DB
                content:
                    application/json:
                        schema: VideoAnalysisSchema
            404: 
                description: Empty database
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
        output = gv.api_dm.document_router.get_last_video_analysis_document()
        # Response
        response = json.dumps(output)
    except Exception as e:
        gv.logger.error(e)
        status=500
        output = utils.build_output(task=cfg.get_last_document_task, status=500,
                                        message=str(e), output={})
        response = json.dumps(output)
    return response, status