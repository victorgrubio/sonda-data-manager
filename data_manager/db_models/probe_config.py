import mongoengine as me


class ProbeConfig(me.Document):
    url = me.StringField(default="udp://224.0.1.4:5678", description="URL where the video is being played")
    program_number = me.IntField(description="Program number in multiplex")
    mode = me.StringField(default="complete", description="Mode of analysis")
    journey_start_time = me.IntField(default=0, description="Offset start for journey, in minutes")
    journey_duration = me.IntField(default=1440, description="Duration of journey, in minutes")
    program_duration = me.IntField(default=60, description="Duration of program if no EPG is provided, in minutes")
    channel_name = me.StringField(default="NEW CHANNEL", description="Name of channel analysed")
    epg_channel_name = me.StringField(default="None", description="Name of EPG channel for the analysis.")
    alert_mos_threshold = me.FloatField(default=2.0, description="Upper MOS threshold to raise a MOS alert. Lower threshold, not inclusive, to raise a warning")
    warning_mos_threshold = me.FloatField(default=2.5, description="Upper MOS threshold to raise a MOS warning")
    samples = me.IntField(default=-1, description="Number of samples to be analysed. -1 to infinite")
    mos_regular = me.FloatField(default=1.7, description="Upper MOS threshold (not inclusive) for poor MOS category. Lower threshold for regular MOS category")
    mos_good = me.FloatField(default=2.7, description="Upper MOS threshold (not inclusive) for regular MOS category. Lower threshold for good MOS category")
    mos_excellent = me.FloatField(default=4.2, description="Lower MOS threshold for excellent MOS category.")
