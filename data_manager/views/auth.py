from flask import Blueprint, abort, request, jsonify
from helper import global_variables as gv
from helper import config as cfg
from helper import utils
import json
from bson import json_util
import  os

auth = Blueprint('auth', __name__, url_prefix="/videoAnalysis/auth")

def is_user_valid(user_data):
    gv.logger.info(os.getenv("VIDEOMOS_PASSWORD"))
    if user_data["user"] == os.getenv("VIDEOMOS_USER") and user_data["password"] == os.getenv("VIDEOMOS_PASSWORD"):
        return True
    return False

@auth.route('/login', methods=['POST'])
def api_auth_login():
    """
    post:
        tags: 
        -  auth
        summary: Logs in
        description: Gets the auth in JSON format
        operationId: get_doc_by_id
        parameters: 
        -   name: api_key
            in: header
            required: false
            schema:
                type: string
        -   name: file
            in: formData
            description: auth in JSON file with valid schema
            required: true
            type: file
        responses: 
            200:
                description: auth imported successfully
                content:
                    application/json:
                        schema: ApiResponse
            405: 
                description: Invalid input
                content:
                    application/json:
                        schema: ErrorResponse
       security: 
        -  api_key: 
    """
    status = 200
    try:
        request_data = request.get_json(force=True)
        if is_user_valid(request_data):
            # check if the post request has the file part
            output = utils.build_output(task="Login", status=200,
                                            message="Successfull operatiom", output={})
            response = jsonify(output)
        else:
            raise AttributeError("Invalid credentials")
    except Exception as e:
        gv.logger.error(e)
        status = 401
        output = utils.build_output(task="Login", status=401,
                                        message="Invalid credentials", output={})
        response = json.dumps(output)
    return response, status


@auth.route('/logout', methods=['POST'])
def api_auth_logout():
    """
    post:
        tags: 
        -  auth
        summary: Gets the auth in JSON format
        description: Gets the auth in JSON format
        operationId: get_doc_by_id
        parameters: 
        -   name: api_key
            in: header
            required: false
            schema:
                type: string
        -   name: file
            in: formData
            description: auth in JSON file with valid schema
            required: true
            type: file
        responses: 
            200:
                description: auth imported successfully
                content:
                    application/json:
                        schema: ApiResponse
            405: 
                description: Invalid input
                content:
                    application/json:
                        schema: ErrorResponse
       security: 
        -  api_key: 
    """
    status = 200
    try:
        # check if the post request has the file part
        output = utils.build_output(task="Logout", status=200,
                                        message="Successfull operatiom", output={})
        response = jsonify(output)
    except Exception as e:
        gv.logger.error(e)
        status=401
        output = utils.build_output(task="LOGIN", status=500,
                                        message=str(e), output={})
        response = json.dumps(output)
    return response

@auth.route('/user', methods=['GET'])
def api_auth_user():
    """
    get:
        tags: 
        -  auth
        summary: Gets the auth in JSON format
        description: Gets the auth in JSON format
        operationId: get_doc_by_id
        parameters: 
        -   name: api_key
            in: header
            required: false
            schema:
                type: string
        -   name: file
            in: formData
            description: auth in JSON file with valid schema
            required: true
            type: file
        responses: 
            200:
                description: auth imported successfully
                content:
                    application/json:
                        schema: ApiResponse
            405: 
                description: Invalid input
                content:
                    application/json:
                        schema: ErrorResponse
       security: 
        -  api_key: 
    """
    status = 200
    try:
        user = {"user": os.getenv("VIDEOMOS_USER")}
        response = jsonify(user)
    except Exception as e:
        gv.logger.error(e)
        return abort(status=401, description=str(e))
    return response, status