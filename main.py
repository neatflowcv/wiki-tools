import asyncio
import json
from dotenv import load_dotenv
import os
import click
import wiki

load_dotenv()

wiki_api_url = os.getenv("WIKI_API_URL")
wiki_api_key = os.getenv("WIKI_API_KEY")


def ensure_credentials() -> tuple[str, str]:
    if not wiki_api_url or not wiki_api_key:
        raise click.ClickException(
            "WIKI_API_URL 및 WIKI_API_KEY 환경 변수가 필요합니다."
        )
    return wiki_api_url, wiki_api_key


async def list_pages_command():
    url, key = ensure_credentials()
    pages = await wiki.list_pages(url, key)
    click.echo(
        json.dumps(
            [page.__dict__ for page in pages],
            ensure_ascii=False,
            indent=2,
        )
    )


async def rename_pages_command(old_path: str, new_path: str):
    url, key = ensure_credentials()
    pages = await wiki.list_pages(url, key)
    targets = [page for page in pages if page.is_parent_path(old_path)]

    if not targets:
        raise click.ClickException(f"{old_path} 경로를 사용하는 페이지가 없습니다.")

    for target in targets:
        new_target_path = new_path + target.path[len(old_path) :]

        while any(page.is_equal_path(new_target_path) for page in pages):
            new_target_path = new_target_path + "_dup"

        click.echo(f"{target.path} -> {new_target_path}")
        await wiki.move_page(url, key, target, new_target_path)


@click.group()
def cli():
    """위키 페이지 관리 CLI"""
    pass


@cli.command("list")
def list_command():
    """모든 페이지를 조회합니다."""
    asyncio.run(list_pages_command())


@cli.command("rename")
@click.argument("old_path")
@click.argument("new_path")
def rename_command(old_path: str, new_path: str):
    """old_path 이하의 페이지를 new_path로 이동합니다."""
    asyncio.run(rename_pages_command(old_path, new_path))


if __name__ == "__main__":
    cli()
