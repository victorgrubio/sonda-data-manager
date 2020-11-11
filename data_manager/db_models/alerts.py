import mongoengine as me
from datetime import datetime

class Alert(me.Document):
    journey_datetime = me.DateTimeField(description="Datetime of journey (identifier) for this object")
    program_name = me.StringField(description="Name of program")
    document_id = me.ObjectIdField(db_field="video_analysis")
    description = me.StringField(default="Brief description of alert", description="Brief description of alert")
    start_datetime = me.DateTimeField(default=datetime.now, description="Initial datetime of alert")
    end_datetime = me.DateTimeField(default=datetime.now, description="Final datetime of alert")
    duration = me.IntField(description="duration in samples", default=1)
    category = me.StringField(description="Type of alert", unique_with=['document_id'])
    confidence = me.FloatField(description="Percentage of accuracy of the alert", default=0)
    mos = me.FloatField(description="Average mos value during the alert", default=0.0)
    url = me.StringField(default="images/alert_mos.png", description="URL for the website to show the alert's icon")
    init_sample_frame = me.IntField(description="Initial frame in measure where alert has appeared")
    video_second = me.IntField(description="Second of video where the alert is produced. Only for VOD")

class Warn(me.Document):
    journey_datetime = me.DateTimeField(description="Datetime of journey (identifier) for this object")
    program_name = me.StringField(description="Name of program")
    document_id = me.ObjectIdField(db_field="video_analysis")
    description = me.StringField(default="Brief description of alert", description="Brief description of alert")
    start_datetime = me.DateTimeField(default=datetime.now, description="Initial datetime of alert")
    end_datetime = me.DateTimeField(default=datetime.now, description="Final datetime of alert")
    duration = me.IntField(description="duration in samples", default=1)
    category = me.StringField(description="Type of alert", unique_with=['document_id'])
    confidence = me.FloatField(description="Percentage of accuracy of the alert", default=0)
    mos = me.FloatField(description="Average mos value during the alert", default=0.0)
    url = me.StringField(default="images/warning_mos.png", description="URL for the website to show the alert's icon")
    init_sample_frame = me.IntField(description="Initial frame in measure where alert has appeared")
    video_second = me.IntField(description="Second of video where the alert is produced. Only for VOD")