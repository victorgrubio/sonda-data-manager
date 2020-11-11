from flask import Blueprint, jsonify, request
from helper import global_variables as gv
from helper import config as cfg
import traceback
from helper import utils

probe = Blueprint('probe', __name__, url_prefix="/videoAnalysis/probe")


@probe.route('/modes', methods=['GET'])
def api_get_probe_modes():
    """
    Get VideoQualityProbe modes
    ---
    get:
        tags:
            -  others
        summary:  Gets available modes from probe
        description: Gets available modes from probe
        operationId: get_probe_modes
        parameters:
            - name: api_key
              in: header
              required: false
              schema:
                type: string
        responses:
            200:
                description: Probe modes
                content:
                    application/json:
                        schema:
                            type: array
                            items:
                                type: integer
            default:
                description: Unexpected server response
                content:
                    application/json: ErrorResponse
        security:
            -  api_key:
    """
    response = ""
    status = 200
    try:
        response = {"probe_modes": cfg.probe_modes}
        # Response
    except Exception as e:
        gv.logger.error(e)
        response = utils.build_output(task=cfg.launch_videoqualityprobe, status=500,
                                        message=str(e), output={})
    return jsonify(response), status

@probe.route("/launch", methods=["POST"])
def api_launch_videoqualityprobe():
    """
    Get file from a provided filename
    ---
    post:
        tags:
            - videoqualityprobe
        summary: Launchs Video Quality Probe
        description: Video Quality Probe starts analyzing video
        operationId: launch_videoqualityprobe
        parameters:
            -   name: api_key
                in: header
                required: false
                schema:
                    type: string
        responses:
            200:
                description: Video Quality Probe launched successfully
                content:
                    application/json:
                        schema: ApiResponse
            404:
                description: VideoQualityProbe config not found
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
    response = ""
    try:
        gv.api_dm.probe_router.launch_videoqualityprobe()
        response = utils.build_output(task=cfg.launch_videoqualityprobe, status=200,
                                    message=cfg.success_msg, output={})
    except AttributeError:
        status = 404
        gv.logger.error(e)
        response = utils.build_output(task=cfg.launch_videoqualityprobe, status=status,
                                        message=str(e), output={})
    except Exception as e:
        gv.logger.error(e)
        response = utils.build_output(task=cfg.launch_videoqualityprobe, status=500,
                                        message=str(e), output={})
    return jsonify(response), status


@probe.route('/stop', methods=['POST'])
def api_stop_videoqualityprobe():
    """"
    Get file from a provided filename
    ---
    post:
        tags:
            - videoqualityprobe
        summary: Stops Video Quality Probe
        description: Video Quality Probe stops analyzing video
        operationId: stop_videoqualityprobe
        parameters:
            -   name: api_key
                in: header
                required: false
                schema:
                    type: string
        responses:
            200:
                description: Video Quality Probe stopped successfully
                content:
                    application/json:
                        schema: ApiResponse
            404:
                description: VideoQualityProbe not started yet
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
        gv.api_dm.probe_router.stop_videoqualityprobe()
        response = utils.build_output(task=cfg.stop_videoqualityprobe, status=200,
                                        message=cfg.success_msg, output={})
    except Exception as e:
        gv.logger.error(e)
        status = 500
        response = utils.build_output(task=cfg.stop_videoqualityprobe, status=500,
                                        message=str(e), output={})
    return jsonify(response), status


@probe.route('/config', methods=['GET'])
def api_get_config_videoqualityprobe():
    """
    Get file from a provided filename
    ---
    get:
        tags:
            - videoqualityprobe
        summary: Gets config of VideoQualityProbe
        description: Gets the current configuration of the VideoQualityProbe
        operationId: get_config_videoqualityprobe
        parameters:
            -   name: api_key
                in: header
                required: false
                schema:
                    type: string
        responses:
            200:
                description: Configuration of Video Quality Probe
                content:
                    application/json:
                        schema: ProbeConfigSchema
            404:
                description: Config not found on server
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
    response = {}
    task = "Get videoqualityprobe config"
    try:
        return gv.api_dm.config_router.get_config_videoqualityprobe(), 200
    except AttributeError:
        status = 200
        gv.logger.error(e)
        response = utils.build_output(task=task, status=status,
                                        message=str(e), output={})
    except Exception as e:
        gv.logger.error(e)
        response = utils.build_output(task=task, status=500,
                                        message=str(e), output={})
    return jsonify(response), status


@probe.route('/config', methods=['PUT'])
def api_put_config_videoqualityprobe():
    """
    Updates config
    ---
    put:
        tags:
            - videoqualityprobe
        summary: Put new config for probe
        description: Updates current config
        operationId: put_config_videoqualityprobe
        requestBody:
            description: Config for videoqualityprobe
            required: true
            content:
                application/json:
                    schema: ProbeConfigSchema
        parameters:
            -   name: api_key
                in: header
                required: false
                schema:
                    type: string
        responses:
            200:
                description: Config updated successfully
                content:
                    application/json:
                        schema: ApiResponse
            default:
                description: Unexpected server response
                content:
                    application/json:
                        schema: ErrorResponse
        security:
            -  api_key:
    """
    status = 200
    task = "Put config of videoqualityprobe"
    try:
        config_data = request.get_json(force=True)
        gv.api_dm.config_router.put_config_videoqualityprobe(config_data)
        response = utils.build_output(task=task, status=200,
                                        message="Config added succssfully", output={})
    except Exception as e:
        gv.logger.error(e)
        status = 500
        response = utils.build_output(task=task, status=500,
                                        message=str(e), output={})
    return jsonify(response), status


@probe.route('/status', methods=['GET'])
def api_get_status_videoqualityprobe():
    """
    Returns current status of videoqualityprobe
    ---
    get:
        tags:
            -  videoqualityprobe
        summary: Gets current status of probe
        description: Gets current status of videoqualityprobe
        operationId: get_status_videoqualityprobe
        parameters:
            -   name: api_key
                in: header
                required: false
                schema:
                    type: string
        responses:
            200:
                description: Status of videoqualityprobe
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                status:
                                    type: string
                                    enum: [idle, stopped, running]
                            example:
                                status: running
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
        probe_status = gv.api_dm.probe_status
        if probe_status in ["error", "killed"]:
            gv.logger.warning("Current status: {}".format(probe_status))
        response = {"STATUS": probe_status}
    except Exception as e:
        status = 500
        gv.logger.error(e)
        gv.logger.error(traceback.print_exc())
        response = utils.build_output(task="Get videoqualityprobe status", status=500,
                                        message=str(e), output={})
    return jsonify(response), status


@probe.route('/epg/channels', methods=['GET'])
def api_get_current_epg():
    """
    Get file from a provided filename
    ---
    get:
        tags:
            - videoqualityprobe
        summary: Gets config of VideoQualityProbe
        description: Gets the current configuration of the VideoQualityProbe
        operationId: get_config_videoqualityprobe
        parameters:
            -   name: api_key
                in: header
                required: false
                schema:
                    type: string
        responses:
            200:
                description: Configuration of Video Quality Probe
                content:
                    application/json:
                        schema: ProbeConfigSchema
            404:
                description: Config not found on server
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
    task = "Get EPG channels"
    try:
        channels = gv.api_dm.db_manager.program_manager.epg_manager.channels
        response = channels
    except AttributeError:
        status = 200
        gv.logger.error(e)
        response = utils.build_output(task=task, status=status,
                                        message=str(e), output={})
    except Exception as e:
        gv.logger.error(e)
        status = 500
        response = utils.build_output(task=task, status=500,
                                        message=str(e), output={})
    return jsonify(response), status
