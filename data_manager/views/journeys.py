from flask import Blueprint, jsonify
from helper import global_variables as gv
from helper import config as cfg
from helper import utils
import json
import traceback

journeys = Blueprint('journeys', __name__, url_prefix="/videoAnalysis/journeys")


@journeys.route('/date-list', methods=['GET'])
def api_get_journeys_date_list():
    """
    Gets list of journey datetimes
    ---
    get:
        tags: 
            - journeys
        summary: Gets list of journey datetimes
        description: Returns the list of journey datetimes
        operationId: get_journeys_date_list
        responses: 
            200:
                description: List of journeys start datetimes
                content:
                    application/json:
                        schema:
                            type: array
                            items:
                                type: date-time
            404: 
                description: No journeys in DB
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
    journey_date_list = []
    status = 200
    try:
        journey_date_list = gv.api_dm.journey_router.get_journeys_date_list()
        if journey_date_list == []:
            raise AttributeError("No journeys in DB")
        output = {"journey_date_list": journey_date_list}
        # Response
        response = jsonify(output)
    except AttributeError as e:
        status = 404
        gv.logger.error(e)
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    except Exception as e:
        status = 500
        gv.logger.error(e)
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    return response, status

@journeys.route('/<journey_datetime>/mos', methods=['GET'])
def api_get_journey_mos(journey_datetime):
    """
    Get mos value of specific journey
    ---
    get:
        tags: 
            - journeys
        summary: Gets average mos of a specific journey
        description: Returns the average mos of a specific journey
        operationId: get_journey_mos
        parameters: 
            - name: journey_datetime
              in: path
              required: true
              schema:
                    oneOf:
                        - type: string
                          example: current
                          enum: [current, previous]
                        - type: date-time
        responses: 
            200:
                description: Mos value of journey
                content:
                    application/json:
                        schema: MosSchema
            404: 
                description: Journey not found
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
        journey_data = gv.api_dm.journey_router.get_journey(journey_datetime=journey_datetime)
        if journey_data == {}:
            if journey_datetime in ["current", "previous"]:
                return jsonify({})
            else:
                raise AttributeError("No data for journey with datetime {}".format(journey_datetime))
        output = {"mos": journey_data["mos"]}
        # Response
        response = jsonify(output)
    
    except AttributeError as e:
        status = 404
        gv.logger.error(e)
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    except Exception as e:
        status = 500
        gv.logger.error(e)
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    return response, status

@journeys.route('/<journey_datetime>/mos-percentages', methods=['GET'])
def api_get_journey_mos_percetages(journey_datetime):
    """
    Get mos categories of specific journey
    ---
    get:
        tags: 
            - journeys
        summary: Gets mos percetanges from a journey
        description: Returns the percetanges of mos categories from a journey
        operationId: get_journey_mos_percetanges
        parameters: 
            - name: journey_datetime
              in: path
              required: true
              schema:
                    oneOf:
                        - type: string
                          example: current
                          enum: [current, previous]
                        - type: date-time
        responses: 
            200:
                description: Mos categories of journey
                content:
                    application/json:
                        schema: MosPercentagesSchema
            404: 
                description: Journey not found
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
        journey_data = gv.api_dm.journey_router.get_journey(journey_datetime=journey_datetime)
        if journey_data == {}:
            if journey_datetime in ["current", "previous"]:
                return jsonify({})
            else:
                raise AttributeError("No data for journey with datetime {}".format(journey_datetime))
        output = json.loads(journey_data["mos_percentages"].to_json())
        # Response
        response = jsonify(output)
    except AttributeError as e:
        status = 404
        gv.logger.error(e)
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    except Exception as e:
        status = 500
        gv.logger.error(e)
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    return response, status

@journeys.route('/<journey_datetime>/alert-number', methods=['GET'])
def api_get_journey_alert_number(journey_datetime):
    """
    Gets number of alerts/warnings in journey
    ---
    get:
        tags: 
            - journeys
        summary: Gets number of alerts/warnings in journey
        description: Returns the number of alerts/warnings in a concretejourney
        operationId: get_journey_alert_number
        parameters: 
            - name: journey_datetime
              in: path
              required: true
              schema:
                    oneOf:
                        - type: string
                          example: current
                          enum: [current, previous]
                        - type: date-time
        responses: 
            200:
                description: Alert categories with count
                content:
                    application/json:
                        schema: AlertNumberSchema
            404: 
                description: Journey not found
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
        alerts = gv.api_dm.alert_router.get_alert_warning_number(journey_datetime=journey_datetime)
        # Response
        response = jsonify(alerts)
    except AttributeError as e:
        status = 404
        gv.logger.error(e)
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    except Exception as e:
        status = 500
        gv.logger.error(e)
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    return response, status

@journeys.route('/<journey_datetime>/alert-list', methods=['GET'])
def api_get_journey_alert_list(journey_datetime):
    """
    Gets alerts/warnings details in journey
    ---
    get:
        tags: 
            - journeys
        summary:  Gets alerts/warnings details in journey
        description: Returns the details of alerts and warnings of a concrete journey
        operationId: get_journey_alert_list
        parameters: 
            - name: journey_datetime
              in: path
              required: true
              schema:
                    oneOf:
                        - type: string
                          example: current
                          enum: [current, previous]
                        - type: date-time
        responses: 
            200:
                description: List of alerts and warnings
                content:
                    application/json:
                        schema: AlertListSchema
            404: 
                description: Journey not found
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
        alert_list = gv.api_dm.alert_router.get_alert_warning_list(journey_datetime=journey_datetime)
        # Response
        response = jsonify(alert_list)
    except AttributeError as e:
        status = 404
        gv.logger.error(e)
        gv.logger.error(traceback.print_exc())
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    except Exception as e:
        status = 500
        gv.logger.error(e)
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    return response, status


@journeys.route('/<journey_datetime>/program-list', methods=['GET'])
def api_get_journey_program_list(journey_datetime):
    """
    Gets data of all programs in journey
    ---
    get:
        tags: 
            - journeys
        summary: Gets data of all programs in journey
        description: Gets data of all programs in journey
        operationId: get_journey_program_list
        parameters: 
            - name: journey_datetime
              in: path
              required: true
              schema:
                    oneOf:
                        - type: string
                          example: current
                          enum: [current, previous]
                        - type: date-time
        responses: 
            200:
                description: Data of programs from journey
                content:
                    application/json:
                        schema: 
                            type: array
                            items:
                                schema: ProgramSchema
            404: 
                description: Journey not found
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
        response = json.dumps(gv.api_dm.journey_router.get_journey_program_list(journey_datetime=journey_datetime))
        # Response
    except AttributeError as e:
        status = 404
        gv.logger.error(e)
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    except Exception as e:
        status = 500
        gv.logger.error(e)
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    return response, status

@journeys.route('/<journey_datetime>/program-name-list', methods=['GET'])
def api_get_journey_program_name_list(journey_datetime):
    """
    Gets names of all programs in journey
    ---
    get:
        tags: 
            - journeys
        summary: Gets names of all programs in journey
        description: Gets names of all programs in journey
        operationId: get_journey_program_name_list
        parameters: 
            - name: journey_datetime
              in: path
              required: true
              schema:
                    oneOf:
                        - type: string
                          example: current
                          enum: [current, previous]
                        - type: date-time
        responses: 
            200:
                description: List of programs names
                content:
                    application/json:
                        schema:
                            type: array
                            items:
                                type: string
                                description: Program name
                                example: News
            404: 
                description: Journey not found
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
        program_name_list = gv.api_dm.journey_router.get_journey_program_name_list(journey_datetime=journey_datetime)
        # Response
        response = jsonify(program_name_list)
    except AttributeError as e:
        status = 404
        gv.logger.error(e)
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    except Exception as e:
        status = 500
        gv.logger.error(e)
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    return response, status



@journeys.route('/<journey_datetime>/<program_name>', methods=['GET'])
def api_get_journey_program(journey_datetime, program_name):
    """
    Gets data of a concrete program in journey
    ---
    get:
        tags: 
            - journeys
        summary: Gets data of a concrete program in journey
        description: Gets data of a concrete program in journey
        operationId: get_journey_program
        parameters: 
            - name: journey_datetime
              in: path
              required: true
              schema:
                    oneOf:
                        - type: string
                          example: current
                          enum: [current, previous]
                        - type: date-time
            - name: program_name
              in: path
              required: true
              schema:
                    type: string
                    description: Program name
                    example: News 
        responses: 
            200:
                description: Program from journey
                content:
                    application/json:
                        schema: ProgramSchema
            404: 
                description: Journey not found
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
        program = gv.api_dm.program_router.get_processed_program(journey_datetime=journey_datetime, program_name=program_name)
        # Response
        response = jsonify(program)
        
    except AttributeError as e:
        status = 404
        gv.logger.error(e)
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    except Exception as e:
        status = 500
        gv.logger.error(e)
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    return response, status


"""
NOT USED METHODS

"""


@journeys.route('/<journey_datetime>', methods=['GET'])
def api_get_journey(journey_datetime):
    """
    Get data of complete journey
    ---
    get:
        tags: 
            - journeys
        summary: Gets data of complete journey
        description: Gets data of complete journey
        operationId: get_journey
        parameters: 
            - name: journey_datetime
              in: path
              required: true
              schema:
                type: date-time
        responses: 
            200:
                description: Journey requested
                content:
                    application/json:
                        schema:
                            type: JourneySchema
            404: 
                description: Journey not found
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
        output = {"COMPLETE JOURNEY DATA": "Data from complete yourney should be here"}
        # Response
        response = jsonify(output)
    except AttributeError as e:
        status = 404
        gv.logger.error(e)
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    except Exception as e:
        status = 500
        gv.logger.error(e)
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    return response, status