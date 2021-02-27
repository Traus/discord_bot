TENOR_API = 'WUUCF2M4J7H6'


class GetDict(dict):
    def __getattr__(self, item):
        return self.get(item)


channels = GetDict(
    CHARTER=810172230267830312,
    RULES=809900106585079838,
    INFO=809888611389931551,
    GUILD=809869724413853706,
    COUNCILS=809912063128109096,
    REQUEST=809911949952548874,
    JOIN=810172448195477574,
    GUEST=809869724413853708,
    MEMES=810088859282440202,
)

roles = GetDict(
    MUTED=811149529231130655,
    STRIKE_1=810588368756408340,
    STRIKE_2=810588805790564352,
    STRIKE_3=810588816884236329,
    GUEST=809909397505441851,
    RECRUIT=810525096505770025,
)

members = GetDict(
    TRAUS=444930675045433376,
    ROFL=533927436761563137,
    FANATIK=584083289178898511,
)
