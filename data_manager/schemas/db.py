'''
Created on Dec 4, 2019

@author: visiona2
'''

from marshmallow import Schema, fields
from schemas import video_data, config

class VideoDataCollection(Schema):
    documents = fields.Nested(video_data.VideoAnalysisSchema)

class ConfigCollection(Schema):
    documents = fields.Nested(config.ProbeConfigSchema)

class Database(Schema):
    video_data = fields.Nested(VideoDataCollection)

