import discord
from discord import utils
from discord.embeds import EmptyEmbed


def box(msg: str) -> str:
    return f"```css\n{msg}```" if msg else '<a:no:845581984277069865>'


async def send_by_bot(ctx, *args, delete=False, **kwargs) -> discord.WebhookMessage:
    webhooks = await ctx.message.channel.webhooks()
    webhook = utils.get(webhooks, name="Imposter NQN")
    if webhook is None:
        webhook = await ctx.message.channel.create_webhook(name="Imposter NQN")

    msg = await webhook.send(' '.join(args), wait=True, username=ctx.message.author.name, avatar_url=ctx.message.author.avatar_url, **kwargs)
    if delete:
        await ctx.message.delete()
    return msg


def create_embed(
        title: str = EmptyEmbed,
        description: str = '',
        color: discord.Color = None,
        fields: list = None,
        image: str = EmptyEmbed,
        thumbnail: str = EmptyEmbed,
        footer: str = '',
) -> discord.Embed:
    embed = (discord.Embed(
        title=title,
        description=description,
        color=color or discord.Color.random())
    )
    if fields is not None:
        for field in fields:
            embed.add_field(name=field[0], value=field[1], inline=bool(field[-1]))

    embed.set_image(url=image)
    embed.set_thumbnail(url=thumbnail)
    embed.set_footer(text=footer)

    return embed
