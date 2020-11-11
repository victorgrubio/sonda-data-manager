from flask import Blueprint, jsonify, abort, request
from helper import global_variables as gv
from helper import config as cfg
from helper import utils
from schemas.program import ProgramSchema
import json

programs = Blueprint('programs', __name__, url_prefix="/videoAnalysis/programs")



@programs.route('/<program_name>/data', methods=['GET'])
def api_get_program_data(program_name):
    """
    Get data values of specific program
    ---
    get:
        tags: 
            - programs
        summary: Gets data of specific program
        description: Gets data of specific program
        operationId: get_program_data
        parameters: 
            - name: program_name
              in: path
              required: true
              schema:
                type: string
                example: news1
        responses: 
            200:
                description: Program data
                content:
                    application/json:
                        schema: ProgramDataSchema
            404: 
                description: Program not found
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
        # Checks if the user has specified a journey datetime for the program
        if "journey_datetime" in request.args:
            pass
        program_db = gv.api_dm.program_router.get_program(program_name=program_name)
        if program_db in [None, {}]:
            raise AttributeError("Program {} not found".format(program_name))
        # Response
        program = json.loads(program_db.to_json())
        response = jsonify(program["data"])
    except AttributeError as e:
        status = 404
        gv.logger.error(e)
        abort(status=status, description=str(e))
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    except Exception as e:
        status = 500
        gv.logger.error(e)
        abort(status=status)
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    return response, status


@programs.route('/<program_name>/mos', methods=['GET'])
def api_get_program_mos(program_name):
    """
    Gets average MOS value of specific program
    ---
    get:
        tags: 
            - programs
        summary: Gets average MOS value of specific program
        description: Gets average MOS value of specific program
        operationId: get_program_mos
        parameters: 
            - name: program_name
              in: path
              required: true
              schema:
                type: string
                example: news1
        responses: 
            200:
                description: Program MOS
                content:
                    application/json:
                        schema: MosSchema
            404: 
                description: Program not found
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
        # Checks if the user has specified a journey datetime for the program
        if "journey_datetime" in request.args:
            pass
        output = {"mos": 0.0}
        program = gv.api_dm.program_router.get_program(program_name=program_name)
        if program in [None, {}]:
            if program_name in ["current", "previous"]:
                return jsonify({})
            else:
                raise AttributeError("Program {} not found".format(program_name))
        output = {"mos": program.mos}
        # Response
        response = jsonify(output)
        
    except AttributeError as e:
        status = 404
        gv.logger.error(e)
        abort(status=status, description=str(e))
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    except Exception as e:
        status = 500
        gv.logger.error(e)
        abort(status=status)
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    return response, status

@programs.route('/<program_name>/mos-percentages', methods=['GET'])
def api_get_program_mos_percentages(program_name):
    """
    Gets MOS categories of specific program
    ---
    get:
        tags: 
            - programs
        summary: Gets MOS categories of specific program
        description: Gets MOS categories of specific program
        operationId: get_program_mos_percentages
        parameters: 
            - name: program_name
              in: path
              required: true
              schema:
                type: string
                example: news1
        responses: 
            200:
                description: Program MOS categories
                content:
                    application/json:
                        schema: MosPercentagesSchema
            404: 
                description: Program not found
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
        # Checks if the user has specified a journey datetime for the program
        if "journey_datetime" in request.args:
            pass
        program = gv.api_dm.program_router.get_program(program_name=program_name)
        # If program is empty
        if program in [None, {}]:
            # If it is current/previous, then return empty dict to avoid recurrent errors
            if program_name in ["current", "previous"]:
                return jsonify({})
            else:
                raise AttributeError("Program {} not found".format(program_name))
        # Response
        response = program.mos_percentages.to_json()
        
    except AttributeError as e:
        status = 404
        gv.logger.error(e)
        abort(status=status, description=str(e))
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    except Exception as e:
        status = 500
        gv.logger.error(e)
        abort(status=status)
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    return response, status

@programs.route('/<program_name>/alert-number', methods=['GET'])
def api_get_program_alert_number(program_name):
    """
    Gets number of alerts/warnings of specific program
    ---
    get:
        tags: 
            - programs
        summary: Gets number of alerts/warnings of specific program
        description: Gets number of alerts/warnings of specific program
        operationId: get_program_alert_number
        parameters: 
            - name: program_name
              in: path
              required: true
              schema:
                type: string
                example: news1
        responses: 
            200:
                description: Number of alerts in program
                content:
                    application/json:
                        schema: AlertNumberSchema
            404: 
                description: Program not found
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
    try:
        # Checks if the user has specified a journey datetime for the program
        if "journey_datetime" in request.args:
            pass
        alerts = gv.api_dm.alert_router.get_alert_warning_number(program_name=program_name)
        # Response
        response = jsonify(alerts)
    except AttributeError as e:
        status = 404
        gv.logger.error(e)
        abort(status=status, description=str(e))
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    except Exception as e:
        status = 500
        gv.logger.error(e)
        abort(status=status)
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    return response

@programs.route('/<program_name>/alert-list', methods=['GET'])
def api_get_program_alert_list(program_name):
    """
    Gets a list of alerts/warnings of specific program
    ---
    get:
        tags: 
            - programs
        summary: Gets a list of alerts/warnings of specific program
        description: Gets a list of alerts/warnings of specific program
        operationId: get_program_alert_list
        parameters: 
            - name: program_name
              in: path
              required: true
              schema:
                type: string
                example: news1
        responses: 
            200:
                description: List of alerts/warnings of specific program
                content:
                    application/json:
                        schema: AlertListSchema
            404: 
                description: Program not found
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
        # Checks if the user has specified a journey datetime for the program
        if "journey_datetime" in request.args:
            pass
        alerts = gv.api_dm.alert_router.get_alert_warning_list(program_name=program_name)
        # Response
        response = jsonify(alerts)
    except AttributeError as e:
        status = 404
        gv.logger.error(e)
        abort(status=status, description=str(e))
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    except Exception as e:
        status = 500
        gv.logger.error(e)
        abort(status=status)
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = json.dumps(output)
    return response, status



