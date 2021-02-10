from discord import Member, Guild, TextChannel, Message
from discord.ext import commands


class Detectors(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def should_ignore(self, guild: Guild, member: Member, channel: TextChannel):
        try:
            config = self.bot.cfg.load(guild.id)["exempt"]
        except:
            return True

        if member.bot:
            return True

        if member.id in config.get("users", []):
            return True

        if channel.id in config.get("channels", []):
            return True

        if channel.category and channel.category.id in config.get("categories", []):#
            return True

        user_roles = [role.id for role in member.roles]
        exempt_rolees = config.get("roles", [])

        if set(user_roles) & set(exempt_rolees):
            return True

        return False

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if not message.guild:
            return
        if self.should_ignore(message.guild, message.author, message.channel):
            return


def setup(bot: commands.Bot):
    bot.add_cog(Detectors(bot))