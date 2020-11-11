from marshmallow import fields
from marshmallow_mongoengine import ModelSchema
import db_models

from schemas.mos import MosPercentagesSchema

class VideoSettingsSchema(ModelSchema):
    class Meta:
        model = db_models.VideoSettings


class AudioSettingsSchema(ModelSchema):
    class Meta:
        model = db_models.AudioSettings


class MosAnalysisSchema(ModelSchema):
    class Meta:
        model = db_models.MosAnalysis


class VideoSRCSchema(ModelSchema):
    class Meta:
        model = db_models.VideoSRC


class VideoAnalysisSchema(ModelSchema):
    class Meta:
        model = db_models.VideoAnalysis
    
    videoSRC = fields.Nested(VideoSRCSchema)
    videoSettings = fields.Nested(VideoSettingsSchema)
    audioSettings = fields.Nested(AudioSettingsSchema)
    mosAnalysis = fields.Nested(MosAnalysisSchema)