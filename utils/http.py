from aiohttp import ClientSession
from os import environ as env

TOKEN = env["API_KEY"]
BASE = env["URL"]
TOX = BASE + "/api/v1/toxicity"
NSFW = BASE + "/api/v1/nsfw"

headers = {
    "Authorization": TOKEN
}


class DetectorClient:
    def __init__(self):
        self.sess = ClientSession(headers=headers)

    async def ensure(self):
        if self.sess.closed:
            self.sess = ClientSession(headers=headers)

    async def toxic(self, text: str):
        async with self.sess.post(TOX, json={"text":text}) as resp:
            return await resp.json()

    async def nsfw(self, url: str):
        async with self.sess.post(NSFW, json={"url":url}) as resp:
            return await resp.json()
