from yaml import safe_load
from pathlib import Path

class Loader:
    def __init__(self):
        self.cache = {}

    def flush(self, guild: int = None):
        if guild:
            del self.cache[guild]
            return
        self.cache = {}

    def load(self, guild: int) -> dict:
        p = Path(f"./guilds/{guild}.yml")

        if not p.exists(): return {}

        with p.open(encoding="utf-8") as f:
            data = safe_load(f)

        self.cache[guild] = data
        return data

    def reload(self, guild: int) -> dict:
        self.flush(guild)
        return self.load(guild)
