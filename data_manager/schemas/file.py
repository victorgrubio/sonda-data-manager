'''
Created on Dec 4, 2019

@author: visiona2
'''

from marshmallow import Schema, fields
from schemas import mos, video_data, alert

class FileDetailsSchema(Schema):
    name = fields.String(description="Name of file", default="Video1", required=True)
    mos_percentages = fields.Nested(mos.MosPercentagesSchema)
    alerts = fields.Integer(description="Number of alerts", default=0)
    warnings = fields.Integer(description="Number of warnings", default=0)
    video_src = fields.Nested(video_data.VideoSRCSchema)
    video_settings = fields.Nested(video_data.VideoSettingsSchema)
    audio_settings = fields.Nested(video_data.AudioSettingsSchema)
    alert_list = fields.Nested(alert.AlertSchema, many=True)
    warning_list = fields.Nested(alert.WarningSchema, many=True)
    

class FileThumbnailSchema(Schema):
    thumbnail_path = fields.String(description="Path to video thumbnail", default="thumbnail.jpg")
    name = fields.String(description="Name of video file", default="Video1.mp4")
    mos = fields.Nested(mos.MosSchema)
    

class FileListSchema(Schema):
    file_list = fields.Nested(FileThumbnailSchema, many=True)
