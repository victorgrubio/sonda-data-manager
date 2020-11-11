import mongoengine as me
from db_models.mos_percentages import MosPercentages


class Journey(me.Document):
    journey_datetime = me.DateTimeField(description="Datetime of journey (identifier) for this object")
    mos = me.FloatField(description="Average MOS of journey")
    mos_percentages = me.EmbeddedDocumentField(MosPercentages, description="Array of percentages for MOS categories")
    measures = me.IntField(description="Measures")
    duration = me.IntField(description="Duration of journey in minutes")
    program_duration = me.IntField(description="Duration of programs in minutes if EPG is not provided")
    content_type = me.StringField(description="type of content: vod or live", default="live")