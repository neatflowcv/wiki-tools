import aiohttp
import argparse
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

    def is_parent_path(self, path: str) -> bool:
        paths = self.path.split("/")
        parents = path.split("/")
        return paths[: len(parents)] == parents

    def is_equal_path(self, path: str) -> bool:
        return self.path == path


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


async def move_page(url: str, key: str, page: WikiPage, new_path: str):
    print(f"Moving page {page.id} {page.path} to {new_path}")
    payload = {
        "query": "mutation MovePage($id: Int!, $destPath: String!, $destLocale: String!) { pages { move(id: $id, destinationPath: $destPath, destinationLocale: $destLocale) { responseResult { succeeded message } } } }",
        "variables": {
            "id": page.id,
            "destPath": new_path,
            "destLocale": page.locale,
        },
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            headers={"Authorization": f"Bearer {key}"},
            json=payload,
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()
            print(data)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="위키 페이지 경로를 old_path에서 new_path로 이동합니다."
    )
    parser.add_argument("old_path", help="이동할 기존 페이지 경로")
    parser.add_argument("new_path", help="새 페이지 경로")
    return parser.parse_args()


async def main():
    args = parse_args()

    if not wiki_api_url or not wiki_api_key:
        raise RuntimeError("WIKI_API_URL 및 WIKI_API_KEY 환경 변수가 필요합니다.")

    pages = await list_pages(wiki_api_url, wiki_api_key)
    targets = [page for page in pages if page.is_parent_path(args.old_path)]
    print(targets)

    tasks = []
    for target in targets:
        new_path = args.new_path + target.path[len(args.old_path) :]

        # pages 중에 new_path와 동일한 경로가 있는지 확인
        if any(page.is_equal_path(new_path) for page in pages):
            new_path = new_path + "_dup"

        tasks.append(
            asyncio.create_task(move_page(wiki_api_url, wiki_api_key, target, new_path))
        )

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
