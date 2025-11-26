import aiohttp
import asyncio
from dataclasses import dataclass
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()

wiki_api_url = os.getenv("WIKI_API_URL")
wiki_api_key = os.getenv("WIKI_API_KEY")


@dataclass
class WikiPage:
    id: str
    path: str
    title: str


async def list_pages(url: str, key: str) -> list[WikiPage]:
    payload = {"query": "query { pages { list { id path title } } }"}
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
        WikiPage(id=page["id"], path=page["path"], title=page["title"])
        for page in pages
    ]


def main():
    pages = asyncio.run(list_pages(wiki_api_url, wiki_api_key))
    st.json([page.__dict__ for page in pages])


if __name__ == "__main__":
    main()
