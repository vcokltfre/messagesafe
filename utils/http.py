from aiohttp import ClientSession
from os import environ as env


class DetectorClient:
    def __init__(self):
        self.TOKEN = env["API_KEY"]
        self.BASE = env["URL"]
        self.TOX = self.BASE + "/api/v1/toxicity"
        self.NSFW = self.BASE + "/api/v1/nsfw"

        self.headers = {
            "Authorization": self.TOKEN
        }

        self.sess = ClientSession(headers=self.headers)

    async def ensure(self):
        if self.sess.closed:
            self.sess = ClientSession(headers=self.headers)

    async def toxic(self, text: str):
        async with self.sess.post(self.TOX, json={"text":text}) as resp:
            return await resp.json()

    async def nsfw(self, url: str):
        async with self.sess.post(self.NSFW, json={"url":url}) as resp:
            return await resp.json()
