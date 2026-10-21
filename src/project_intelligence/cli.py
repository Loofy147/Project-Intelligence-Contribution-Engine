"""Command-line entry point for the Project Intelligence Engine."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from project_intelligence.indexer import (
    DEFAULT_MAX_FILE_BYTES,
    build_index,
    load_index,
)
from project_intelligence.search import search_index


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pie",
        description="Index local project text and search it with ranked results.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    index_parser = subcommands.add_parser("index", help="build a local project index")
    index_parser.add_argument("root", nargs="?", default=".", help="project directory")
    index_parser.add_argument(
        "--output",
        type=Path,
        help="index destination (default: ROOT/.project-intelligence/index.json)",
    )
    index_parser.add_argument(
        "--max-file-bytes",
        type=int,
        default=DEFAULT_MAX_FILE_BYTES,
        help=f"skip larger files (default: {DEFAULT_MAX_FILE_BYTES})",
    )

    search_parser = subcommands.add_parser("search", help="search an existing index")
    search_parser.add_argument("query", help="search terms; quote multiword phrases")
    search_parser.add_argument(
        "--index",
        type=Path,
        default=Path(".project-intelligence/index.json"),
        help="path to the JSON index",
    )
    search_parser.add_argument("--limit", type=int, default=10, help="maximum results")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "index":
            root = Path(args.root).expanduser().resolve()
            output = args.output
            if output is None:
                output = root / ".project-intelligence" / "index.json"
            index = build_index(
                root,
                max_file_bytes=args.max_file_bytes,
                output_path=output,
            )
            print(
                f"Indexed {index['files_indexed']} files; "
                f"skipped {index['files_skipped']}. Index: "
                f"{Path(output).expanduser().resolve()}"
            )
            print("Review the generated index before sharing it; it contains file text.")
            return 0

        index = load_index(args.index)
        results = search_index(index, args.query, limit=args.limit)
        if not results:
            print("No matching documents.")
            return 0

        for rank, result in enumerate(results, start=1):
            print(f"{rank}. {result['path']}  (score: {result['score']:.4f})")
            print(f"   {result['snippet']}")
        return 0

    except (OSError, ValueError) as exc:
        print(f"pie: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
