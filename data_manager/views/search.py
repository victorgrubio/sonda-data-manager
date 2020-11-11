from flask import Blueprint, jsonify, abort, request
from helper import global_variables as gv
from helper import config as cfg
from helper import utils
import json
import traceback

search = Blueprint('search', __name__, url_prefix="/videoAnalysis/search")

@search.route('/data', methods=['POST'])
def api_search_data():
    """
    Returns data from a given date range or journey search
    ---
    post:
        tags: 
            - search
        summary: Returns data from a given date range or journey search
        description: Returns data from a given date range or journey search
        operationId: search_data
        requestBody:
            description: Data for search - Datetimes, Journey, Program and URL.
            required: true
            content:
                application/json:
                    schema:
                        oneOf:
                            - SearchDatetimeSchema
                            - SearchJourneySchema
        responses: 
            200:
                description: Search results
                content:
                    application/json:
                        schema:
                            oneOf:
                                - MosSchema
                                - MosPercentagesSchema
            404: 
                description: No documents in search range
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
        body_data = request.get_json(force=True)
        output = gv.api_dm.historic_router.get_historic_search(body_data)
        # Response
        response = jsonify(output)
    except Exception as e:
        gv.logger.error(e)
        gv.logger.error(traceback.print_exc())
        status = 500
        output = utils.build_output(task=cfg.get_documents_by_datetime_range, status=500,
                                        message=str(e), output={})
        response = json.dumps(output)
    return response, status

@search.route('/url', methods=['POST'])
def api_search_url():
    """
    Returns data from a given date range or journey search
    ---
    post:
        tags: 
            - search
        summary: Returns data from a given date range or journey search
        description: Returns data from a given date range or journey search
        operationId: search_data
        requestBody:
            description: Data for search - Datetimes, Journey, Program and URL.
            required: true
            content:
                application/json:
                    schema:
                        oneOf:
                            - SearchDatetimeSchema
                            - SearchJourneySchema
        responses: 
            200:
                description: Url for file resulting from search process
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                url:
                                    type: string
                                    example: /files/fjoaidjfslfjkdfja43124.csv
                                    description: url of file to retrieve
                            required:
                                - url

            404: 
                description: No documents in search range
                content:
                    application/json:
                        schema: ErrorResponse
            default:
                description: Unexpected server response
                content:
                    application/json: ErrorResponse
        security: 
            -  api_key: 
    """
    status = 200
    try:
        body_data = request.get_json(force=True)
        file_url = gv.api_dm.historic_router.get_historic_search_url(body_data)
        response = jsonify({"url": file_url})
    except Exception as e:
        gv.logger.error(e)
        gv.logger.error(traceback.print_exc())
        status = 500
        output = utils.build_output(task=cfg.get_documents_by_datetime_range, status=500,
                                        message=str(e), output={})
        response = json.dumps(output)
    return response, status