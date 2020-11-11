from marshmallow import Schema, fields
from marshmallow_mongoengine import ModelSchema
import db_models
from schemas.mos import MosPercentagesSchema

class ProgramSchema(ModelSchema):
    class Meta:
        model = db_models.Program
    mos_percentages = fields.Nested(MosPercentagesSchema)


class ProgramDataSchema(Schema):
    mos = fields.Float(description="MOS value", default=1.0)
    pts = fields.Integer(description="PTS value", default=0)
    timestamp = fields.String(description="Timestamp of measure")