from marshmallow import Schema, fields, post_load

class Anomaly(object):
    def __init__(self, strategy, scores, init_pts, end_pts, window_size, window_overlap):
        self.strategy = strategy
        self.scores = scores
        self.init_pts = init_pts
        self.end_pts = end_pts
        self.window_size = window_size
        self.window_overlap = window_overlap

    def __repr__(self):
        return f'<Anomaly[{self.strategy}]>'

class AnomalySchema(Schema):
    strategy = fields.String(description="Strategy followed to detect anomalies")
    scores = fields.List(fields.Float(description="Confidence of having an alert"))
    init_pts = fields.Integer(description="Initial pts of the anomaly")
    end_pts = fields.Integer(description="Final pts of the anomaly")
    window_size = fields.Integer(description="Size of window to detect anomalies")
    window_overlap = fields.Integer(description="Number of samples overlapping for each window")

    @post_load
    def make_anomaly(self, data):
        return Anomaly(**data)

class InputAnomalyDataSchema(Schema):
    temp_inf = fields.List(fields.Float, description="List of temp inf data")
    blurring = fields.List(fields.Float, description="List of blurring data")
    pts = fields.List(fields.Integer, description="List of pts")
    timestamp = fields.Integer(description="Timestamp of initial sample from measure")
