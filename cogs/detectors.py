from asyncio import get_event_loop, sleep
from discord import Member, Guild, TextChannel, Message, Embed
from discord.ext import commands
from discord.utils import get

action_values = {
    "null": 0,
    "alert": 1,
    "delete": 2,
}

embed_template = """[**Jump to Message**]({jump}) - {author} ({author.id})

**__Snippet:__**
```
{snippet}
```

**__Detection Values:__**
{vals}

**__Actions Taken:__**
"""


class Detectors(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.loop = get_event_loop()

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

    def toxicity_embed(self, message: Message, scores: dict, ops: list) -> Embed:
        title = f"ToxWarn | {message.guild} -> #{message.channel}"

        jump = str(message.jump_url)
        snippet = message.content[:1024]
        vals = "\n".join([f"{k}: {round(v, 3)}" for k, v in scores.items()])

        desc = embed_template.format(jump=jump, snippet=snippet, author=message.author, vals=vals)
        embed = Embed(title=title, colour=0xFF0000, description=desc)

        for op in ops:
            action = op["action"]
            extra = "No Extra Data"
            if op:
                for k, v in op.items():
                    if k != "action":
                        extra = f"{k}: {v}"
                        break
            embed.add_field(name=action, value=extra)

        return embed

    async def mute_user(self, role: int, member: Member, duration: int):
        if not role: return
        await member.add_roles(get(member.guild.roles, id=role))
        await sleep(duration)
        await member.remove_roles(get(member.guild.roles, id=role))

    async def logsend(self, guild: Guild, logtype: str, embed: Embed = None, content: str = None):
        config = self.bot.cfg.load(guild.id).get("logs", {})

        if not config:
            return

        channel = guild.get_channel(config.get(logtype))

        if not channel:
            return

        await channel.send(content=content, embed=embed)

    async def execute_toxic_op(self, message: Message, op: dict, scores: dict, ops: list, mute_role: int):
        try:
            if op["action"] == "alert":
                await self.logsend(message.guild, "toxic", embed=self.toxicity_embed(message, scores, ops))

            elif op["action"] == "delete":
                await message.delete()

            elif op["action"] == "dm":
                content = op["message"]

                for k, v in scores.items():
                    if k in content:
                        content = content.format(value=round(v, 3))
                await message.author.send(content)

            elif op["action"] == "mute":
                await self.mute_user(mute_role, message.author, op["duration"])
        except Exception as e:
            print(f"Failed to execute action {op['action']}: {e}")

    async def execute_toxic(self, message: Message, scores: dict):
        config = self.bot.cfg.load(message.guild.id)

        if not config:
            return

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

        for op in ops:
            self.loop.create_task(self.execute_toxic_op(message, op, scores, ops, config.get("muted_role")))

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if not message.guild:
            return
        if self.should_ignore(message.guild, message.author, message.channel):
            return

        await self.execute_toxic(message, await self.bot.detector.toxic(message.content))

    @commands.command(name="reload_guild")
    @commands.check_any(commands.has_guild_permissions(manage_guild=True), commands.is_owner())
    async def reload_guild(self, ctx):
        self.bot.cfg.reload(ctx.guild.id)
        await ctx.send(f"Successfully reloaded guild config for {ctx.guild.id}.")


def setup(bot: commands.Bot):
    bot.add_cog(Detectors(bot))