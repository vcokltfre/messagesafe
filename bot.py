from templatebot import Bot
from dotenv import load_dotenv
from os import environ as env
from discord import Intents

load_dotenv(".env")

bot = Bot(name="MessageSafe", command_prefix=env.get("PREFIX", "~"), intents=Intents.all())
bot.load_initial_cogs()

bot.run(env["TOKEN"])