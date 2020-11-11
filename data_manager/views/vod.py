from flask import Blueprint, jsonify, abort, request
from werkzeug.utils import secure_filename

import uuid
import json
import os

from helper import global_variables as gv
from helper import config as cfg
from helper import utils


vod = Blueprint('vod', __name__, url_prefix="/videoAnalysis/vod")


@vod.route('/upload', methods=['POST'])
def api_vod_upload():
    """
    Uploads file to server for VOD analysis
    ---
    get:
        tags: 
            - vod
        summary: Uploads file to server for VOD analysis
        description: Uploads file to server for VOD analysis
        operationId: vod_upload
        responses: 
            200:
                description: URL of uploaded file in server
                content:
                    application/json:
                        schema:
                            type: string
                            example: /tmp/video1.mkv
            400: 
                description: File already in server
                content:
                    application/json:
                        schema: ErrorResponse
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
        if 'file' not in request.files:
            raise AttributeError("No file has been sent to the API")
        video_file = request.files['file']
        filename = secure_filename(video_file.filename)
        file_uuid = uuid.uuid4()
        file_save_path = "{}/{}_{}".format(cfg.upload_path, file_uuid.hex[:8], filename)
        if os.path.exists(file_save_path):
            raise FileExistsError("File already in server. Please set url as /tmp/FILE_NAME to run videoqualityprobe")
        gv.logger.info("File saved at {}".format(file_save_path))
        video_file.save(file_save_path)
        status = 200
        # Response
        output = { "video_path": file_save_path }
        response = jsonify(output)
    except FileExistsError as e:
        status = 400
        gv.logger.error(e)
        abort(status=status, description=str(e))
        output = utils.build_output(task="Upload video", status=status,
                                        message=str(e), output={})
        response = jsonify(output)
    except AttributeError as e:
        status = 404
        gv.logger.error(e)
        abort(status=status, description=str(e))
        output = utils.build_output(task="Upload video", status=status,
                                        message=str(e), output={})
        response = jsonify(output)
    except Exception as e:
        status = 500
        gv.logger.error(e)
        abort(status=status)
        output = utils.build_output(task=cfg.get_journey_data, status=status,
                                        message=str(e), output={})
        response = jsonify(output)
    return response, status
