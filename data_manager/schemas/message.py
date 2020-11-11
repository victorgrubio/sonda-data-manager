from marshmallow import Schema, fields

class ApiResponse(Schema):
    code = fields.Integer(default=200)
    task = fields.String(default="Example of task")
    message = fields.String(description="Information about the operation")
    output = fields.Dict()

class ErrorResponse(Schema):
    code = fields.Integer(default=500)
    task = fields.String(default="Example of task")
    message = fields.String(description="Information about the operation")
    output = fields.Dict()