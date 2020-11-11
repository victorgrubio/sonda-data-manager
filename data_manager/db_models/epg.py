import mongoengine as me


class EpgProgram(me.EmbeddedDocument):
    program_name = me.StringField(description="Name of program", required=True)
    channel = me.StringField(description="Channel where this program is shown", required=True)
    start_datetime = me.DateTimeField(description="Start time of program", required=True)
    end_datetime = me.DateTimeField(description="End time of program", required=True)
    duration = me.IntField(description="duration of program, in minutes")

class Epg(me.Document):
    journey_datetime = me.DateTimeField(description="Date of this epg", required=True)
    provider = me.StringField(description="EPG generator")
    channels = me.ListField(me.StringField(description="Channel name"), description="List of channels in EPG")
    programs = me.EmbeddedDocumentListField(EpgProgram, description="List of programs at EPG")
    created_at = me.DateTimeField(description="Time when epg was created")
    