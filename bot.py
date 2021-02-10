from templatebot import Bot
from dotenv import load_dotenv
from os import environ as env
from discord import Intents

from utils.config import Loader
from utils.http import DetectorClient

load_dotenv(".env")

bot = Bot(name="MessageSafe", command_prefix=env.get("PREFIX", "~"), intents=Intents.all())
bot.cfg = Loader()
bot.detector = DetectorClient()
bot.load_initial_cogs("cogs.detectors")

bot.run(env["TOKEN"])