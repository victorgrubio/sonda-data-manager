from marshmallow_mongoengine import ModelSchema
from marshmallow import fields, Schema
import db_models

class MosPercentagesSchema(ModelSchema):
    class Meta:
        model = db_models.MosPercentages

class MosSchema(Schema):
    mos = fields.Float(default=1.0, description="Mos Value")