import argparse
import asyncio
import json
from dotenv import load_dotenv
import os
import wiki

load_dotenv()

wiki_api_url = os.getenv("WIKI_API_URL")
wiki_api_key = os.getenv("WIKI_API_KEY")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="위키 페이지 경로를 old_path에서 new_path로 이동합니다."
    )
    parser.add_argument("old_path", help="이동할 기존 페이지 경로")
    parser.add_argument("new_path", help="새 페이지 경로")
    return parser.parse_args()


async def main():
    # args = parse_args()

    if not wiki_api_url or not wiki_api_key:
        raise RuntimeError("WIKI_API_URL 및 WIKI_API_KEY 환경 변수가 필요합니다.")

    pages = await wiki.list_pages(wiki_api_url, wiki_api_key)
    # targets = [page for page in pages if page.is_parent_path(args.old_path)]
    print(
        json.dumps(
            [page.__dict__ for page in pages],
            ensure_ascii=False,
            indent=2,
        )
    )

    # for target in targets:
    #     new_path = args.new_path + target.path[len(args.old_path) :]

    #     # pages 중에 new_path와 동일한 경로가 있는지 확인
    #     if any(page.is_equal_path(new_path) for page in pages):
    #         new_path = new_path + "_dup"

    #     await wiki.move_page(wiki_api_url, wiki_api_key, target, new_path)


if __name__ == "__main__":
    asyncio.run(main())
