import asyncio
from typing import Optional

import aiohttp


class Deezer:
    ROOT_URL = "https://api.deezer.com"

    def __init__(self) -> None:
        pass

    def search(self, artist: Optional[str], album: Optional[str]) -> list:
        params = {"q": [], "index": 0, "limit": 1}
        if artist:
            params["q"].append(f'artist:"{artist}"')
        if album:
            params["q"].append(f'album:"{album}"')
        params["q"] = " ".join(params["q"])

        async def impl():
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.ROOT_URL}/search", params=params
                ) as response:
                    print(f"RESP: {response.url}")
                    json = await response.json()
                    return json["data"]

        return asyncio.run(impl())
