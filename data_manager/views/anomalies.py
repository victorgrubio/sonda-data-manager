import traceback
import json
from flask import Blueprint, abort, request
from schemas.anomaly import AnomalySchema

from helper import utils
from helper import global_variables as gv
from helper import config as cfg

anomalies = Blueprint('anomalies', __name__, url_prefix="/videoAnalysis/anomalies")

@anomalies.route('/', methods=['POST'])
def api_send_anomaly_data():
    """
    post:
        tags: 
        -  anomaly
        summary: Send data to detect anomalies
        description: Send data to detect anomalies using VideoQPrediction module
        operationId: send_anomaly_data
        requestBody:
            description: Frame by frame data for anomaly detection
            required: true
            content:
                application/json:
                    schema: InputAnomalyDataSchema
        responses: 
            200:
                description: Data for anomaly detection received
                content:
                    application/json:
                        schema: AnomalySchema
            500: 
                description: Internal Server Error
                content:
                    application/json:
                        schema: ErrorResponse
       security: 
        -  api_key: 
    """
    try:
        request_data = request.get_data()
        request_data_dict = json.loads(request_data.decode("utf-8"))
        timestamp = request_data_dict.pop("timestamp")
        response_vqpred = gv.api_dm.videoqualitypred_manager.send_anomaly_data(request_data_dict)
        anomaly = AnomalySchema().load(response_vqpred.json()).data
        gv.api_dm.alert_router.check_anomaly_results(timestamp, anomaly)
        output = utils.build_output(task="Send anomaly information", status=200,
                                        message="Data has been sent for anomaly analysis", output={})
        return json.dumps(output), 200
    except Exception as e:
        gv.logger.error(e)
        output = utils.build_output(task="Internal server error", status=500,
                                        message=str(e), output={})
        return json.dumps(output), 500
    