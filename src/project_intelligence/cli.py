"""Command-line entry point for the Project Intelligence Engine."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from project_intelligence.ai_review import review_tasks
from project_intelligence.indexer import (
    DEFAULT_MAX_FILE_BYTES,
    build_index,
    load_index,
)
from project_intelligence.inventory import build_inventory, write_inventory
from project_intelligence.github_issues import fetch_github_issues, write_issue_snapshot
from project_intelligence.github_pulls import fetch_github_pull_requests, write_pull_request_snapshot
from project_intelligence.workplan import build_workplan, load_snapshot, write_workplan
from project_intelligence.search import search_index
from project_intelligence.snapshot_diff import compare_snapshots, write_snapshot_diff
from project_intelligence.source_relations import fetch_explicit_relationships, write_relationship_report
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

    issues_parser = subcommands.add_parser(
        "github-issues",
        help="read-only snapshot of issues from a public GitHub repository",
    )
    issues_parser.add_argument("repository", help="public GitHub OWNER/REPO")
    issues_parser.add_argument("--state", choices=("open", "closed", "all"), default="open")
    issues_parser.add_argument("--json-output", type=Path, help="JSON snapshot path")
    issues_parser.add_argument("--markdown-output", type=Path, help="Markdown index path")
    issues_parser.add_argument("--timeout", type=float, default=20.0, help="per-request timeout in seconds")

    pulls_parser = subcommands.add_parser(
        "github-pulls",
        help="read-only snapshot of pull requests from a public GitHub repository",
    )
    pulls_parser.add_argument("repository", help="public GitHub OWNER/REPO")
    pulls_parser.add_argument("--state", choices=("open", "closed", "all"), default="open")
    pulls_parser.add_argument("--json-output", type=Path, help="JSON snapshot path")
    pulls_parser.add_argument("--markdown-output", type=Path, help="Markdown report path")
    pulls_parser.add_argument("--timeout", type=float, default=20.0, help="per-request timeout in seconds")

    workplan_parser = subcommands.add_parser(
        "workplan",
        help="prioritize existing GitHub records separately from draft findings",
    )
    workplan_parser.add_argument("--issues", type=Path, required=True, help="issue snapshot JSON")
    workplan_parser.add_argument("--pulls", type=Path, help="optional pull-request snapshot JSON")
    workplan_parser.add_argument("--tasks", type=Path, help="optional task-draft JSON")
    workplan_parser.add_argument("--json-output", type=Path, help="JSON workplan output")
    workplan_parser.add_argument("--markdown-output", type=Path, help="Markdown workplan output")

    diff_parser = subcommands.add_parser(
        "compare-snapshots",
        help="compare two read-only GitHub issue/PR snapshots without inferring completion",
    )
    diff_parser.add_argument("--previous-issues", type=Path, required=True, help="previous issue snapshot JSON")
    diff_parser.add_argument("--current-issues", type=Path, required=True, help="current issue snapshot JSON")
    diff_parser.add_argument("--previous-pulls", type=Path, help="optional previous pull-request snapshot JSON")
    diff_parser.add_argument("--current-pulls", type=Path, help="optional current pull-request snapshot JSON")
    diff_parser.add_argument("--json-output", type=Path, help="JSON comparison output path")
    diff_parser.add_argument("--markdown-output", type=Path, help="Markdown comparison report path")

    relations_parser = subcommands.add_parser(
        "github-relations",
        help="audit explicit GitHub timeline cross-references without inferring issue/PR links",
    )
    relations_parser.add_argument("--issues", type=Path, help="public GitHub issue snapshot JSON")
    relations_parser.add_argument("--pulls", type=Path, help="public GitHub pull-request snapshot JSON")
    relations_parser.add_argument("--timeout", type=float, default=20.0, help="per-request timeout in seconds")
    relations_parser.add_argument("--max-records", type=int, default=50, help="maximum snapshot records to inspect (1-500)")
    relations_parser.add_argument("--json-output", type=Path, help="JSON relationship report path")
    relations_parser.add_argument("--markdown-output", type=Path, help="Markdown relationship report path")

    ai_parser = subcommands.add_parser(
        "ai-review", help="optionally request a metadata-only review through OmniRoute Workbench"
    )
    ai_parser.add_argument(
        "--tasks", type=Path, default=Path(".project-intelligence/tasks.json"),
        help="task JSON file (default: .project-intelligence/tasks.json)",
    )
    ai_parser.add_argument(
        "--output", type=Path, default=Path(".project-intelligence/ai-review.json"),
        help="advisory JSON output path (default: .project-intelligence/ai-review.json)",
    )
    ai_parser.add_argument("--base-url", help="local Workbench base URL; defaults to PIE_AI_BASE_URL or loopback")
    ai_parser.add_argument("--timeout", type=float, default=60.0, help="gateway timeout in seconds (maximum 180)")
    ai_parser.add_argument("--max-tasks", type=int, default=20, help="maximum candidates to send (1-50)")
    ai_parser.add_argument(
        "--allow-remote", action="store_true",
        help="allow a non-loopback AI gateway; task metadata will leave this machine",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "compare-snapshots":
            if (args.previous_pulls is None) != (args.current_pulls is None):
                raise ValueError("Both --previous-pulls and --current-pulls must be supplied together")
            previous_issues = load_snapshot(args.previous_issues, "issues")
            current_issues = load_snapshot(args.current_issues, "issues")
            previous_pulls = load_snapshot(args.previous_pulls, "pull_requests") if args.previous_pulls else None
            current_pulls = load_snapshot(args.current_pulls, "pull_requests") if args.current_pulls else None
            diff = compare_snapshots(previous_issues, current_issues, previous_pulls, current_pulls)
            json_path = args.json_output or Path(".project-intelligence/snapshot-diff.json")
            markdown_path = args.markdown_output or Path(".project-intelligence/snapshot-diff.md")
            write_snapshot_diff(diff, json_path, format="json")
            write_snapshot_diff(diff, markdown_path, format="markdown")
            summary = diff["summary"]
            print(
                f"Compared {diff['repository']}: "
                f"{summary['issue_records_changed']} changed issues, "
                f"{summary['pull_request_records_changed']} changed pull requests."
            )
            print(f"JSON: {json_path.expanduser().resolve()}")
            print(f"Report: {markdown_path.expanduser().resolve()}")
            print("Read-only comparison. Absence does not imply closure, deletion, or completion.")
            return 0

        if args.command == "github-relations":
            if args.issues is None and args.pulls is None:
                raise ValueError("Supply at least one of --issues or --pulls")
            issue_snapshot = load_snapshot(args.issues, "issues") if args.issues else None
            pull_snapshot = load_snapshot(args.pulls, "pull_requests") if args.pulls else None
            source_snapshots = [snapshot for snapshot in (issue_snapshot, pull_snapshot) if snapshot is not None]
            repository = source_snapshots[0]["source"]["repository"]
            if any(snapshot["source"]["repository"].casefold() != repository.casefold() for snapshot in source_snapshots):
                raise ValueError("Issue and pull-request snapshots must refer to the same repository")

            targets = []
            for item in (issue_snapshot["issues"] if issue_snapshot else []):
                if not isinstance(item, dict):
                    raise ValueError("Issue snapshot contains a non-object record")
                targets.append({
                    "record_type": "issue",
                    "number": item.get("number"),
                    "title": item.get("title", ""),
                })
            for item in (pull_snapshot["pull_requests"] if pull_snapshot else []):
                if not isinstance(item, dict):
                    raise ValueError("Pull-request snapshot contains a non-object record")
                targets.append({
                    "record_type": "pull_request",
                    "number": item.get("number"),
                    "title": item.get("title", ""),
                })

            report = fetch_explicit_relationships(
                repository, targets, timeout=args.timeout, max_records=args.max_records
            )
            report["input_snapshots"] = [
                {
                    "repository": snapshot["source"]["repository"],
                    "endpoint": snapshot["source"].get("endpoint"),
                    "query_state": snapshot["source"].get("query_state"),
                    "fetched_at": snapshot["source"].get("fetched_at"),
                    "record_count": len(snapshot["issues"] if "issues" in snapshot else snapshot["pull_requests"]),
                }
                for snapshot in source_snapshots
            ]
            json_path = args.json_output or Path(".project-intelligence/github-relations.json")
            markdown_path = args.markdown_output or Path(".project-intelligence/github-relations.md")
            write_relationship_report(report, json_path, format="json")
            write_relationship_report(report, markdown_path, format="markdown")
            summary = report["summary"]
            print(
                f"Audited {summary['targets_scanned']} timelines in {repository}: "
                f"{summary['explicit_in_repository_relations']} explicit in-repository relationships, "
                f"{summary['external_or_unverified_references']} external/unverified references."
            )
            print(f"JSON: {json_path.expanduser().resolve()}")
            print(f"Report: {markdown_path.expanduser().resolve()}")
            print("Read-only audit. No relation is inferred from title similarity; no source record was changed.")
            return 0

        if args.command == "ai-review":
            review = review_tasks(
                args.tasks,
                args.output,
                base_url=args.base_url,
                allow_remote=args.allow_remote,
                timeout=args.timeout,
                max_tasks=args.max_tasks,
            )
            print(
                "AI review wrote " + str(len(review["reviews"])) + " recommendations; "
                + str(review["tasks_omitted_by_limit"]) + " candidates omitted by the task limit."
            )
            print("Advisory report: " + str(args.output.expanduser().resolve()))
            print("No task, source file, GitHub record, XP, or bounty state was changed.")
            return 0

        if args.command == "github-issues":
            snapshot = fetch_github_issues(
                args.repository,
                state=args.state,
                timeout=args.timeout,
            )
            default_prefix = args.repository.replace("/", "--")
            json_path = args.json_output or (
                Path(".project-intelligence") / f"{default_prefix}-issues.json"
            )
            markdown_path = args.markdown_output or (
                Path(".project-intelligence") / f"{default_prefix}-issues.md"
            )
            write_issue_snapshot(snapshot, json_path, format="json")
            write_issue_snapshot(snapshot, markdown_path, format="markdown")
            summary = snapshot["summary"]
            print(
                f"Read {summary['issues_found']} issues from {args.repository}: "
                f"{summary['open']} open, {summary['closed']} closed."
            )
            print(f"JSON: {json_path.expanduser().resolve()}")
            print(f"Report: {markdown_path.expanduser().resolve()}")
            print("Read-only snapshot; no issue was created, changed, or closed.")
            return 0

        if args.command == "github-pulls":
            snapshot = fetch_github_pull_requests(
                args.repository, state=args.state, timeout=args.timeout
            )
            prefix = args.repository.replace("/", "--")
            json_path = args.json_output or (Path(".project-intelligence") / f"{prefix}-pulls.json")
            markdown_path = args.markdown_output or (Path(".project-intelligence") / f"{prefix}-pulls.md")
            write_pull_request_snapshot(snapshot, json_path, format="json")
            write_pull_request_snapshot(snapshot, markdown_path, format="markdown")
            summary = snapshot["summary"]
            print(
                f"Read {summary['pull_requests_found']} pull requests from {args.repository}: "
                f"{summary['open']} open, {summary['drafts']} drafts."
            )
            print(f"JSON: {json_path.expanduser().resolve()}")
            print(f"Report: {markdown_path.expanduser().resolve()}")
            print("Read-only snapshot; no pull request was changed or merged.")
            return 0

        if args.command == "workplan":
            issues = load_snapshot(args.issues, "issues")
            pulls = load_snapshot(args.pulls, "pull_requests") if args.pulls else None
            task_set = load_task_set(args.tasks) if args.tasks else None
            plan = build_workplan(issues, pulls, task_set)
            json_path = args.json_output or Path(".project-intelligence/workplan.json")
            markdown_path = args.markdown_output or Path(".project-intelligence/workplan.md")
            write_workplan(plan, json_path, format="json")
            write_workplan(plan, markdown_path, format="markdown")
            counts = plan["summary"]["issues_by_priority"]
            print(
                f"Workplan for {plan['repository']}: {plan['summary']['existing_issues']} issues "
                f"(P0={counts['P0']}, P1={counts['P1']}), "
                f"{plan['summary']['existing_pull_requests']} pull requests, "
                f"{plan['summary']['draft_tasks']} draft findings."
            )
            print(f"JSON: {json_path.expanduser().resolve()}")
            print(f"Report: {markdown_path.expanduser().resolve()}")
            print("Read-only projection; no external records were created or changed.")
            return 0

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
                f"Wrote {task_set['summary']['total_drafts']} task records "
                f"({task_set['summary']['observed_marker_tasks']} source markers; "
                f"{task_set['summary'].get('observed_checklist_tasks', 0)} checklist items; "
                f"{task_set['summary'].get('registry_work_item_tasks', 0)} canonical registry projections; "
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
