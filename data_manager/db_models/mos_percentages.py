import mongoengine as me

class MosPercentages(me.EmbeddedDocument):
    mos_poor = me.FloatField(description="Percentage of POOR samples", default=25.0)
    mos_regular = me.FloatField(description="Percentage of REGULAR samples", default=25.0)
    mos_good = me.FloatField(description="Percentage of GOOD samples", default=25.0)
    mos_excellent = me.FloatField(description="Percentage of EXCELLENT samples", default=25.0)