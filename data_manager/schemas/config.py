'''
Created on Dec 4, 2019

@author: visiona2
'''
from marshmallow import Schema, fields
from marshmallow_mongoengine import ModelSchema
import db_models


class ProbeConfigSchema(ModelSchema):
    class Meta:
        model = db_models.ProbeConfig