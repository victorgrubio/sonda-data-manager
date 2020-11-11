import traceback
import json
import warnings
import sys
from flask import Flask, request, abort, jsonify, render_template, g
from flask_cors import CORS
from datetime import datetime
from flask_swagger_ui import get_swaggerui_blueprint
from bson import json_util


#Modules for logging
import time

# Custom modules: cfg y globals
from helper import config as cfg
from helper import global_variables as gv
from helper import utils
from helper.cache import cache

# Import views (endpoints)
import views

# Import schemas
from schemas.video_data import VideoAnalysisSchema
from schemas.message import ApiResponse, ErrorResponse

warnings.filterwarnings('ignore')

app = Flask(__name__, template_folder="static/templates")
cache.init_app(app)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_SUPPORTS_CREDENTIALS'] = True
app.config['CORS_ALLOW_HEADERS'] = 'Content-Type, Authorization'
app.config['CORS_EXPOSE_HEADERS'] = 'Content-Type, Authorization'

# Register docs on API
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Video Quality Data Manager"})
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

# Register blueprints for different components
app.register_blueprint(views.auth_view)
app.register_blueprint(views.db_view)
app.register_blueprint(views.documents_view)
app.register_blueprint(views.config_view)
app.register_blueprint(views.files_view)
app.register_blueprint(views.journeys_view)
app.register_blueprint(views.programs_view)
app.register_blueprint(views.search_view)
app.register_blueprint(views.probe_view)
app.register_blueprint(views.vod_view)
app.register_blueprint(views.anomalies_view)


"""DOCS"""
@app.route('/docs', methods=['GET'])
def api_render_docs():
    return render_template('api_docs.html')

@app.route('/docs-pdf', methods=['GET'])
def api_render_docs_pdf():
    return render_template('api_docs_pdf.html')

@app.route('/videoAnalysis/updateFrame', methods=['GET'])
def api_update_frame():
    """
    Updates thumbnail frame from current video
    ---
    get:
        tags: 
            -  others
        summary:  Gets thumbnail frame
        description:  Updates thumbnail frame from current video/stream
        operationId: update_frame
        parameters: 
            - name: api_key
              in: header
              required: false
              schema:
                type: string
        responses: 
            200:
                description: Updated frame succesfully
                content:
                    application/json:
                        schema: ApiResponse
            default:
                description: Unexpected server response
                content:
                    application/json: ErrorResponse
        security: 
            -  api_key: 
    """
    status = 200
    try:
        output = gv.api_dm.update_frame()
        # Response
        response = json.dumps(output)
    except Exception as e:
        gv.logger.error(e)
        status=500
        output = utils.build_output(task=cfg.launch_videoqualityprobe, status=500,
                                        message=str(e), output={})
        response = json.dumps(output)
    return response, status


if __name__ == '__main__':
    try:
        gv.init(parent_dir=cfg.data_manager_path, log_level=cfg.log_level)
    except Exception as e:
        print(e)
    app.run(host=cfg.host,port=cfg.port,debug=False)

else:
    try:
        gv.init(parent_dir=cfg.data_manager_path, log_level=cfg.log_level) 
    except Exception as e:
        print(e)


