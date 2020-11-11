from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

import json
import os
import yaml
from pathlib import Path
from helper import config as cfg

# Reference your schemas definitions
from schemas import video_data, mos, program, alert, journey, message, config, search, anomaly

# Now, reference your routes.
import init_service
import views

# Create spec
spec = APISpec(
    openapi_version="3.0.0",
    title="Swagger Video Analysis",
    version='1.0.0',
    info={
        "description": "This is a Data Manager serer for video quality analysis. The development of this service is provided by GATV, a research group from the Technical University of Madrid.",
        "termsOfService": "http://swagger.io/terms/",
        "contact": {
          "email": "dmz@gatv.ssr.upm.es"
        },
        "license": {
          "name": "Apache 2.0",
          "url": "http://www.apache.org/licenses/LICENSE-2.0.html"
        }
    },
    host = "sonda:{}".format(os.getenv("API_PORT")),
    basePath = "/",
    tags = [
        {
          "name": "documents",
          "description": "Measures of MOS"
        },
        {
          "name": "journeys",
          "description": "Journey related methods"
        },
        {
          "name": "programs",
          "description": "Program related methods"
        },
        {
          "name": "search",
          "description": "Search methods"
        },
        {
          "name": "vod",
          "description": "VoD methods"
        },
        {
          "name": "videoqualityprobe",
          "description": "MOS probe management"
        },
        {
          "name": "database",
          "description": "Database management"
        },
        {
          "name": "anomalies",
          "description": "Anomalies management"
        },
        {
          "name": "others",
          "description": "Additional methods with non-specific category"
        }
    ],
    plugins=[MarshmallowPlugin(), FlaskPlugin()]
)


"""
Definition of schemas


"""
# Standard response
spec.components.schema("ApiResponse", schema=message.ApiResponse)
spec.components.schema("ErrorResponse", schema=message.ErrorResponse)

# Documents
spec.components.schema("VideoAnalysisSchema", schema=video_data.VideoAnalysisSchema)

# MOS
spec.components.schema("MosSchema", schema=mos.MosSchema)
spec.components.schema("MosPercentagesSchema", schema=mos.MosPercentagesSchema)

# Programs
spec.components.schema("ProgramSchema", schema=program.ProgramSchema)

# Alerts
spec.components.schema("AlertListSchema", schema=alert.AlertListSchema)
spec.components.schema("AlertNumberSchema", schema=alert.AlertNumberSchema)

# Config
spec.components.schema('ProbeConfigSchema', schema=config.ProbeConfigSchema)

# Search
spec.components.schema('SearchDatetimeSchema', schema=search.SearchDatetimeSchema)
spec.components.schema('SearchJourneySchema', schema=search.SearchJourneySchema)

# Anomalies
spec.components.schema('InputAnomalyDataSchema', schema=anomaly.InputAnomalyDataSchema)



"""
Add methods from each route

"""
# init_service.py
with init_service.app.test_request_context():
    # others
    spec.path(view=init_service.api_update_frame)
    # files
    spec.path(view=views.files.api_get_file_by_filename)
    # db
    spec.path(view=views.db.api_import_db)
    spec.path(view=views.db.api_export_db)
    # videoqualityprobe
    spec.path(view=views.probe.api_launch_videoqualityprobe)
    spec.path(view=views.probe.api_stop_videoqualityprobe)
    spec.path(view=views.probe.api_get_status_videoqualityprobe)
    spec.path(view=views.probe.api_get_config_videoqualityprobe)
    spec.path(view=views.probe.api_put_config_videoqualityprobe)
    # documents
    spec.path(view=views.documents.api_post_bulk_document)
    spec.path(view=views.documents.api_get_last_document)
    # journey
    spec.path(view=views.journeys.api_get_journey_mos)
    spec.path(view=views.journeys.api_get_journeys_date_list)
    spec.path(view=views.journeys.api_get_journey_mos_percetages)
    spec.path(view=views.journeys.api_get_journey_alert_number)
    spec.path(view=views.journeys.api_get_journey_alert_list)
    spec.path(view=views.journeys.api_get_journey_program_list)
    spec.path(view=views.journeys.api_get_journey_program_name_list)
    spec.path(view=views.journeys.api_get_journey_program)
    # program
    spec.path(view=views.programs.api_get_program_data)
    spec.path(view=views.programs.api_get_program_mos)
    spec.path(view=views.programs.api_get_program_mos_percentages)
    spec.path(view=views.programs.api_get_program_alert_number)
    spec.path(view=views.programs.api_get_program_alert_list)
    # search
    spec.path(view=views.search.api_search_data)
    spec.path(view=views.search.api_search_url)
    # vod
    spec.path(view=views.vod.api_vod_upload)
    # anomalies
    spec.path(view=views.anomalies.api_send_anomaly_data)

"""
Save file

"""
with open(f'{cfg.data_manager_path}/static/swagger.json', 'w') as f:
    json.dump(spec.to_dict(), f)