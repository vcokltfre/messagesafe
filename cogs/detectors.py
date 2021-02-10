from discord import Member, Guild, TextChannel, Message, Embed
from discord.ext import commands

action_values = {
    "null": 0,
    "alert": 1,
    "delete": 2,
}


class Detectors(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def should_ignore(self, guild: Guild, member: Member, channel: TextChannel):
        try:
            config = self.bot.cfg.load(guild.id)["exempt"]
        except Exception as e:
            print("Ignoring", guild.id, "invalid guild.", e)
            return True

        if member.bot:
            print("Ignoring", member.id, "bot user.")
            return True

        if member.id in config.get("users", []):
            print("Ignoring", member.id, "exempt user.")
            return True

        if channel.id in config.get("channels", []):
            print("Ignoring", channel.id, "exempt channel")
            return True

        if channel.category and channel.category.id in config.get("categories", []):
            print("Ignoring", channel.category.id, "exempt category.")
            return True

        user_roles = [role.id for role in member.roles]
        exempt_rolees = config.get("roles", [])

        if set(user_roles) & set(exempt_rolees):
            print("Ignoring", member.id, "has exempt role(s).")
            return True

        return False

    async def logsend(self, channel: TextChannel, embed: Embed):
        if channel:
            await channel.send(embed=embed)

    async def execute_toxic_op(self, message: Message, op: dict, scores: dict):
        if op["action"] == "alert":
            print("Alert:", message.author.id)

        elif op["action"] == "delete":
            print("Delete:", message.channel.id, message.id)

        elif op["action"] == "dm":
            print("DM:", message.author.id, "Content:", op["message"])

        elif op["action"] == "mute":
            print("Mute:", message.author.id, "Duration:", op["duration"])

    async def execute_toxic(self, message: Message, scores: dict):
        config = self.bot.cfg.load(message.guild.id)

        if not config:
            return

        logging = config["logs"]
        values = config["config"]["toxic"]

        top_action = {"name":"null"}

        for name, actions in values.items():
            this_overall = None
            this_upper = 0
            for action in actions:
                if action["value"] < this_upper:
                    continue

                this_upper = action["value"]

                if scores[name] >= this_upper:
                    this_overall = action

            if not this_overall:
                continue

            if action_values[this_overall["action"]["name"]] > action_values[top_action["name"]]:
                top_action = this_overall["action"]

        if top_action["name"] == "null":
            return

        name = top_action["name"]
        ops = top_action["run"]

        print("Message:", message.content)
        print("Actions to take:")

        for op in ops:
            await self.execute_toxic_op(message, op, scores)

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if not message.guild:
            return
        if self.should_ignore(message.guild, message.author, message.channel):
            return

        await self.execute_toxic(message, await self.bot.detector.toxic(message.content))


def setup(bot: commands.Bot):
    bot.add_cog(Detectors(bot))