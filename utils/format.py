import discord
from discord import utils


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
