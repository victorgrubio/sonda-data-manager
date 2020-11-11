import mongoengine as me
from db_models.mos_percentages import MosPercentages


class Program(me.Document):
    journey_datetime = me.DateTimeField(description="Datetime of journey (identifier) for this object")
    program_name = me.StringField(description="Title of program")
    start_datetime = me.DateTimeField(description="Initial datetime of program")
    end_datetime = me.DateTimeField(description="Final datetime of program")
    duration = me.IntField(description="Duration of program in minutes")
    mos = me.FloatField(description="Average MOS value of program")
    mos_percentages = me.EmbeddedDocumentField(MosPercentages, description="Array of percentages for MOS categories")
    url = me.StringField(description="url of input", default="")
    data = me.ListField(me.DictField(default={}), description="Data to draw histogram of program")
    content_type = me.StringField(description="type of content: vod or live", default="live")
    video_settings = me.DictField(description="video settings of program")