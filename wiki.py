from dataclasses import dataclass
import aiohttp


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


async def delete_page(url: str, key: str, page_id: int):
    print(f"Deleting page {page_id}")
    payload = {
        "query": "mutation DeletePage($id: Int!) { pages { delete(id: $id) { responseResult { succeeded message } } } }",
        "variables": {
            "id": page_id,
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

    result = (
        data.get("data", {})
        .get("pages", {})
        .get("delete", {})
        .get("responseResult", {})
    )
    if not result.get("succeeded"):
        raise RuntimeError(
            f"페이지 삭제 실패 (id={page_id}): {result.get('message', '알 수 없는 오류')}"
        )
