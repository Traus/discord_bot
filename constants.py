TENOR_API = 'WUUCF2M4J7H6'
GUILD_ID = 809869724413853706


class _GetDict(dict):
    __getattr__ = dict.__getitem__


channels = _GetDict(
    WELCOME=828238481096310794,
    CHARTER=810172230267830312,
    RULES=809900106585079838,
    INFO=809888611389931551,
    PING=829452523214995467,
    TEST=809896975671623691,
    GUILD=809911906792898590,
    COUNCILS=809912063128109096,
    CARPET=827094235353448468,
    REQUEST=809911949952548874,
    JOIN=810172448195477574,
    GUEST=809869724413853708,
    MEMES=810088859282440202,
    LIST=816617344017235968,
    PRIVATE_CHANNELS=816767538997231656,
    MERY=816769493954985984,
    KEFIR=819920426762240070,
    CHOOSE_CLASS=823293562815774761,
    ALCHIMICS=810135932153757726,
    MAGES=810136042912612382,
    HUNTERS=810136069144182845,
    GUARDS=810136096537051147,
    ROUGES=810136116602601482,
    VOICE=833005450201923614,
    BOTS=827098809334628383,
)


categories = _GetDict(
    PRIVATE=812765587708706866,
)


messages = _GetDict(
    ROOMS=816781266858934304,
    RULES=818831442800410634,
    CHOOSE_CLASS=823296316414754816,
)


roles = _GetDict(
    COUNCILS=809909703123402772,
    TOT=809909642901323777,
    RESERVE=822007579206352906,
    RECRUIT=810525096505770025,
    MUTED=811149529231130655,
    STRIKE_1=810588368756408340,
    STRIKE_2=810588805790564352,
    STRIKE_3=810588816884236329,
    GUEST=809909397505441851,
    DOMINO=815891535849062431,
)

members = _GetDict(
    BOT=810535898701627452,
    TRAUS=444930675045433376,
    ROFL=533927436761563137,
    FANATIK=584083289178898511,
    DOMINO=546365530152632331,
    FOURX=728866034462883862,
)


tavern_emoji = f':regional_indicator_t: ' \
               f':regional_indicator_a: ' \
               f':regional_indicator_v: ' \
               f':regional_indicator_e: ' \
               f':regional_indicator_r: ' \
               f':regional_indicator_n:'


beer_emoji = {
    "<:pepe_beer:828026991361261619>": "beer",
    "<:tavern_beer:822536261079662672>": "ale",
    "<:pepe_celebrate:811749316313350144>": "wine",
    "<:pepe_vodka:811737381551079425>": "vodka",
    "<:honey:847010009874432040>": "honey",
}


vote_reactions = ['<:pepe_yes:811753098867507210>', '<:pepe_no:811753121902362725>']
