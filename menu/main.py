from discord.ext import commands

import config
import ui


class MenuTestBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or(']'))

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


bot = MenuTestBot()


@bot.command()
async def counter(ctx: commands.Context):
    """Starts a counter for pressing."""
    await ctx.send('Press!', view=ui.counter.EphemeralCounter())


@bot.command()
async def servsettings(ctx: commands.Context):
    """Change your server settings."""
    view = ui.servsettings.ServerSettingsUI.new(
        owner=ctx.author,
        settings=ui.servsettings.ServerSettings(),
        guild_name=ctx.guild.name
    )
    await view.send_to(ctx)


@bot.command()
async def csettings(ctx: commands.Context):
    """Change your character's settings (NYI)."""
    await ctx.send('NYI')


if __name__ == '__main__':
    bot.run(config.DISCORD_BOT_TOKEN)
