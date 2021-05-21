import discord
from discord import utils


def box(msg: str) -> str:
    return f"```css\n{msg}```"


async def send_by_bot(ctx, *args, file: discord.File = None, delete=False) -> discord.WebhookMessage:
    webhooks = await ctx.message.channel.webhooks()
    webhook = utils.get(webhooks, name="Imposter NQN")
    if webhook is None:
        webhook = await ctx.message.channel.create_webhook(name="Imposter NQN")

    msg = await webhook.send(' '.join(args), file=file, wait=True, username=ctx.message.author.name, avatar_url=ctx.message.author.avatar_url)
    if delete:
        await ctx.message.delete()
    return msg
