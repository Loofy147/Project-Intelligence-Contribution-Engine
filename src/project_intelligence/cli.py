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
from project_intelligence.inventory import build_inventory, write_inventory
from project_intelligence.search import search_index
from project_intelligence.tasks import (
    generate_draft_tasks,
    load_task_set,
    verify_task_set,
    write_tasks,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pie",
        description="Inventory local projects, search evidence, and draft contribution tasks.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    index_parser = subcommands.add_parser("index", help="build a local project search index")
    index_parser.add_argument("root", nargs="?", default=".", help="project directory")
    index_parser.add_argument("--output", type=Path, help="index destination")
    index_parser.add_argument(
        "--max-file-bytes", type=int, default=DEFAULT_MAX_FILE_BYTES,
        help=f"skip larger files (default: {DEFAULT_MAX_FILE_BYTES})",
    )

    search_parser = subcommands.add_parser("search", help="search an existing index")
    search_parser.add_argument("query", help="search terms; quote multiword phrases")
    search_parser.add_argument(
        "--index", type=Path, default=Path(".project-intelligence/index.json"),
        help="path to the JSON index",
    )
    search_parser.add_argument("--limit", type=int, default=10, help="maximum results")

    inventory_parser = subcommands.add_parser(
        "inventory", help="create a project inventory and review-signal report"
    )
    inventory_parser.add_argument("root", nargs="?", default=".", help="project directory")
    inventory_parser.add_argument("--manifest", type=Path, help="manifest path relative to root or an absolute path")
    inventory_parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    inventory_parser.add_argument("--output", type=Path, help="report destination")
    inventory_parser.add_argument(
        "--max-file-bytes", type=int, default=DEFAULT_MAX_FILE_BYTES,
        help=f"skip larger files (default: {DEFAULT_MAX_FILE_BYTES})",
    )

    tasks_parser = subcommands.add_parser(
        "tasks", help="draft contribution tasks from source markers and inventory hypotheses"
    )
    tasks_parser.add_argument("root", nargs="?", default=".", help="project directory")
    tasks_parser.add_argument("--manifest", type=Path, help="manifest path relative to root or an absolute path")
    tasks_parser.add_argument("--json-output", type=Path, help="JSON output path")
    tasks_parser.add_argument("--markdown-output", type=Path, help="Markdown review report path")
    tasks_parser.add_argument(
        "--max-file-bytes", type=int, default=DEFAULT_MAX_FILE_BYTES,
        help=f"skip larger files (default: {DEFAULT_MAX_FILE_BYTES})",
    )

    verify_parser = subcommands.add_parser(
        "verify-tasks", help="check stored task evidence against a fresh project scan"
    )
    verify_parser.add_argument("root", nargs="?", default=".", help="project directory")
    verify_parser.add_argument(
        "--task-file", type=Path,
        help="task JSON file (default: ROOT/.project-intelligence/tasks.json)",
    )
    verify_parser.add_argument("--manifest", type=Path, help="manifest path relative to root or an absolute path")
    verify_parser.add_argument(
        "--max-file-bytes", type=int, default=DEFAULT_MAX_FILE_BYTES,
        help=f"skip larger files (default: {DEFAULT_MAX_FILE_BYTES})",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "index":
            root = Path(args.root).expanduser().resolve()
            output = args.output or (root / ".project-intelligence" / "index.json")
            index = build_index(root, max_file_bytes=args.max_file_bytes, output_path=output)
            print(
                f"Indexed {index['files_indexed']} files; skipped {index['files_skipped']}. "
                f"Index: {Path(output).expanduser().resolve()}"
            )
            print("The index contains copied file text; review it before sharing.")
            return 0

        if args.command == "search":
            index = load_index(args.index)
            results = search_index(index, args.query, limit=args.limit)
            if not results:
                print("No matching documents.")
                return 0
            for rank, result in enumerate(results, start=1):
                print(f"{rank}. {result['path']}  (score: {result['score']:.4f})")
                print(f"   {result['snippet']}")
            return 0

        if args.command == "inventory":
            root = Path(args.root).expanduser().resolve()
            index = build_index(root, max_file_bytes=args.max_file_bytes)
            inventory = build_inventory(root, index, manifest_path=args.manifest)
            default_name = "inventory.md" if args.format == "markdown" else "inventory.json"
            output = args.output or (root / ".project-intelligence" / default_name)
            written = write_inventory(inventory, output, format=args.format)
            print(
                f"Inventory written to {written}. "
                f"Files indexed: {inventory['summary']['files_indexed']}; "
                f"review hypotheses: {len(inventory['review_signals'])}."
            )
            return 0

        if args.command == "tasks":
            root = Path(args.root).expanduser().resolve()
            index = build_index(root, max_file_bytes=args.max_file_bytes)
            inventory = build_inventory(root, index, manifest_path=args.manifest)
            task_set = generate_draft_tasks(index, inventory)
            json_path = args.json_output or (root / ".project-intelligence" / "tasks.json")
            markdown_path = args.markdown_output or (root / ".project-intelligence" / "tasks.md")
            write_tasks(task_set, json_path, format="json")
            write_tasks(task_set, markdown_path, format="markdown")
            print(
                f"Wrote {task_set['summary']['total_drafts']} draft tasks "
                f"({task_set['summary']['observed_marker_tasks']} observed markers; "
                f"{task_set['summary']['hypothesis_review_tasks']} hypotheses)."
            )
            print(f"JSON: {json_path.expanduser().resolve()}")
            print(f"Review report: {markdown_path.expanduser().resolve()}")
            print("Nothing was published or created as a bounty.")
            return 0

        if args.command == "verify-tasks":
            root = Path(args.root).expanduser().resolve()
            task_file = args.task_file or (root / ".project-intelligence" / "tasks.json")
            task_set = load_task_set(task_file)
            index = build_index(root, max_file_bytes=args.max_file_bytes)
            inventory = build_inventory(root, index, manifest_path=args.manifest)
            report = verify_task_set(index, inventory, task_set)
            summary = report["summary"]
            print(
                f"Checked {summary['total_tasks']} tasks: {summary['fresh']} fresh, "
                f"{summary['stale']} stale, {summary['unverified']} unverified."
            )
            print(
                f"Acceptance criteria missing/incomplete: {summary['missing_acceptance_criteria']}. "
                f"Eligible for execution: {summary['eligible_for_execution']}."
            )
            for item in report["results"]:
                print(
                    f"- {item['freshness'].upper()}: {item['task_id']} — {item['title']} "
                    f"[{item['reason']}; criteria="
                    f"{'complete' if item['acceptance_criteria_complete'] else 'missing'}]"
                )
            return 1 if summary["stale"] or summary["unverified"] else 0

        parser.error("Unknown command")
        return 2
    except (OSError, ValueError) as exc:
        print(f"pie: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
