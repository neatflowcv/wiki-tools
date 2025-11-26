import aiohttp
import asyncio
from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()

wiki_api_url = os.getenv("WIKI_API_URL")
wiki_api_key = os.getenv("WIKI_API_KEY")


@dataclass
class WikiPage:
    id: str
    path: str
    title: str
    locale: str


async def list_pages(url: str, key: str) -> list[WikiPage]:
    payload = {"query": "query { pages { list { id path title locale } } }"}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            headers={"Authorization": f"Bearer {key}"},
            json=payload,
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()

    pages = data.get("data", {}).get("pages", {}).get("list", [])
    return [
        WikiPage(
            id=page["id"], path=page["path"], title=page["title"], locale=page["locale"]
        )
        for page in pages
    ]


async def move_page(page: WikiPage, new_path: str):
    print(f"Moving page {page.id} {page.path} to {new_path}")


def main():
    pages = asyncio.run(list_pages(wiki_api_url, wiki_api_key))
    print(pages)


if __name__ == "__main__":
    main()
