from subprocess import check_output
import os
from pathlib import Path
"""Configuration variables for DataManager
"""
# Web application parameters
# address based on ip of hostname, Enables docker deployment.
host = "0.0.0.0"
port = str(os.getenv("API_PORT"))

# AI Module
ai_host = "0.0.0.0"
ai_port = str(int(os.getenv("API_PORT")) - 1)

# DB
db_name = "VideoDB"
db_host = "127.0.0.1"
db_port = str(os.getenv("DB_PORT"))
collection_name = "video_params"
success_msg = "Successful operation"
error_msg = "An error occurred when processing."


# Tasks
bulk_data_task = "Bulk document into MongoDB"
get_document_id_task = "Get document by ID"
put_document_id_task = "Put document by ID"
delete_document_id_task = "Delete document by ID"
get_last_document_task = "Get last document"
import_db_task = "Import db into MongoDB"
export_db_task = "Export db"
get_documents_by_datetime_range = "Get documents by Datetime range"
launch_videoqualityprobe = "Launch video quality probe"
stop_videoqualityprobe = "Stopped video quality probe"
update_frame = "Frame updated"
get_journey_data = "Get data from specific journey"
get_average_mos = "Get average MOS in a concrete period of time"
get_mos_percentages = "Get MOS categories in a concrete period of time"
get_historic_samples = "Get samples to build the historigram of a datetime range"
get_file_by_filename = "Returns file given a concrete filename"

# General
start_delay = 30.0

# FILES
base_project_path = str(Path(__file__).parent.parent.parent.resolve())
data_manager_path = base_project_path + "/data_manager"
upload_path = "/tmp"

# Dict of file extensions and folders
dict_filetypes = {
    "csv": [".csv"],
    "img": [".png", ".jpg", ".jpeg", ".tiff"],
    "pdf": [".pdf"],
    "json": [".json"]
}

# Dict of allowed filetypes for the historic
historic_filetypes_allowed = ["csv", "json"]

# Dict of filenames for server
dict_server_filenames = {
    "csv_datetime_filename": "historic.csv",
    "json_datetime_filename": "historic.json"
}

# Modes
probe_modes = {
    "fast": "fast",
    "complete": "complete",
    "exhaustive": "exhaustive",
}

#Predict Strategy
predict_strategy = "stacking"

# THRESHOLD BLURRING
blurring_threshold_warning = 25
blurring_threshold_alert = 15

# Alert category and description
dict_alert_category_description = {
    "Video": "No video signal",
    "Audio": "No audio signal",
    "MOS": "Low MOS value",
    "Blurring": "Blurred scene",
    "Content": "Content is unavailable",
    "LostFrames": "Frames lost during streaming"
}

# Probe base config
probe_measure_seconds = "3"
probe_samples = "-1"

#No audio dict
no_audio_settings = {
    "codec" : "unknown",
    "sample_rate" : -99,
    "channels" : -99,
    "bitrate" : -0.000099
}

#Memory limit (MB)
rss_threshold_mb = float(os.getenv("VIDEOMOS_MAX_RAM_MB")) \
    if "VIDEOMOS_MAX_RAM_MB" in os.environ else 1.5*1024

log_level = os.getenv("VIDEOMOS_LOG_LEVEL") \
    if ("VIDEOMOS_LOG_LEVEL" in os.environ and os.getenv("VIDEOMOS_LOG_LEVEL") in ["DEBUG", "INFO", "WARNING", "ERROR"]) \
    else "WARNING"

#Interval time to check health of videoqualityprobe (s)
healthcheck_interval = 10

#Confidence interval
confidence_percentage = 0.95

# VideoQualityPred anomaly thresholds
warning_anomaly_threshold = 0.5
alert_anomaly_threshold = 0.75

process_name = "videoqualityprobe"

playlist_extension = ".mvs"

guide_file = "/opt/data_manager/epg_data/guide.xml"