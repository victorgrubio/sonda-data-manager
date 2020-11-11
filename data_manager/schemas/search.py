from marshmallow import fields, Schema

class SearchJourneySchema(Schema):
    journey_datetime = fields.DateTime(required=True, description="Datetime of journey to search")
    program_name = fields.String(description="Program name to search")
    url = fields.String(description="URL to search")
    type = fields.String(description="Type of file (CSV/JSON)")
    
class SearchDatetimeSchema(Schema):
    start_datetime = fields.DateTime(required=True, description="Start datetime to search")
    end_datetime = fields.DateTime(required=True, description="End datetime to search")
    program_name = fields.String(description="Program name to search")
    url = fields.String(description="URL to search")
    type = fields.String(description="Type of file (CSV/JSON)")
    