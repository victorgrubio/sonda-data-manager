'''
Created on Dec 4, 2019

@author: visiona2
'''

from marshmallow import Schema, fields
from marshmallow_mongoengine import ModelSchema
import db_models


class AlertNumberSchema(Schema):
    """
    
    :param Schema: [description]
    :type Schema: [type]
    """
    alerts = fields.Integer(description="Number of alerts", default=0)
    warnings = fields.Integer(description="Number of warnings", default=0)


class AlertSchema(ModelSchema):
    """[summary]
    
    :param ModelSchema: [description]
    :type ModelSchema: [type]
    """
    class Meta:
        model = db_models.Alert


class WarningSchema(ModelSchema):
    """[summary]
    
    :param ModelSchema: [description]
    :type ModelSchema: [type]
    """
    class Meta:
        model = db_models.Warn
    

class AlertListSchema(Schema):
    """[summary]
    
    :param Schema: [description]
    :type Schema: [type]
    """
    alerts = fields.Nested(AlertSchema, many=True)
    warnings = fields.Nested(WarningSchema, many=True)

