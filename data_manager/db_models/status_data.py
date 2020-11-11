import mongoengine as me
from datetime import datetime


class StatusData(me.Document):
    url = me.StringField(default="udp://224.0.1.4:5678", description="URL where the video is being obtained")
    program_number = me.IntField(description="Program number of channel in multiplex")
    probe_pid = me.IntField(description="PID of probe process")
    process_name = me.StringField(default="videoqualitypro", description="Name of probe process")
    start_datetime = me.DateTimeField(default=datetime.now, description="Datetime where the probe was launched")
    mode = me.StringField(default="complete", description="Analysis mode for the current probe")
    probe_status = me.StringField(default="stopped", description="Status of the current probe")
    last_document_time = me.FloatField(default=0.0, description="Timestamp, in ms, of the last inserted document")
    journey_datetime = me.DateTimeField(default=datetime.now, description="Datetime of journey (identifier) for this object")
    current_program_name = me.StringField(default="", description="Current program name")
    content_type = me.StringField(default="live", description="type of content: vod, live, playlist")
    is_epg_generating = me.BooleanField(default=False, description="Checks if the epg is generating")
  