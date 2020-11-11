from marshmallow import Schema, fields


class JourneyStringSchema(Schema):
    journey_datetime = fields.Float(default=1.0, description="MOS Value")

class JourneyDatetimeSchema(Schema):
    MOS = fields.Float(default=1.0, description="MOS Value")