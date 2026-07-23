from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

from ai_thread_vault.importers import parse_chatgpt, parse_jsonl
from ai_thread_vault.importers.claude import parse as parse_claude
from ai_thread_vault.importers.markdown import parse as parse_markdown
from ai_thread_vault.importers.gemini import parse as parse_gemini
from ai_thread_vault.query import export_markdown, search, show, stats
from ai_thread_vault.schema import init_db


def _cmd_init(args: argparse.Namespace) -> int:
    conn = init_db(args.path)
    conn.close()
    return 0


def _cmd_import(args: argparse.Namespace) -> int:
    parsers = {
        "chatgpt": parse_chatgpt,
        "jsonl": parse_jsonl,
        "claude": parse_claude,
        "markdown": parse_markdown,
        "gemini": parse_gemini,
    }
    import sqlite3
    from ai_thread_vault.clean import clean_thread
    from ai_thread_vault.store import store_thread
    threads = parsers[args.format](args.src)
    conn = sqlite3.connect(args.path)
    n = 0
    for t in threads:
        store_thread(conn, t, clean_thread(t.messages), platform=args.format, source_id=t.id)
        n += 1
    conn.commit(); conn.close()
    print(n)
    return 0


def _cmd_search(args: argparse.Namespace) -> int:
    results = search(args.path, args.query, limit=args.limit)
    print(json.dumps(results))
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    try:
        result = show(args.path, args.thread_id)
    except KeyError:
        return 1
    print(json.dumps(result))
    return 0


def _cmd_export(args: argparse.Namespace) -> int:
    try:
        output = export_markdown(args.path, args.thread_id)
    except KeyError:
        return 1
    sys.stdout.write(output)
    return 0


def _cmd_stats(args: argparse.Namespace) -> int:
    print(json.dumps(stats(args.path)))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("path")
    init_parser.set_defaults(func=_cmd_init)

    import_parser = subparsers.add_parser("import")
    import_parser.add_argument("path")
    import_parser.add_argument("format", choices=["chatgpt", "jsonl", "claude", "markdown", "gemini"])
    import_parser.add_argument("src")
    import_parser.set_defaults(func=_cmd_import)

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("path")
    search_parser.add_argument("query")
    search_parser.add_argument("--limit", type=int)
    search_parser.set_defaults(func=_cmd_search)

    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("path")
    show_parser.add_argument("thread_id")
    show_parser.set_defaults(func=_cmd_show)

    export_parser = subparsers.add_parser("export")
    export_parser.add_argument("path")
    export_parser.add_argument("thread_id")
    export_parser.set_defaults(func=_cmd_export)

    stats_parser = subparsers.add_parser("stats")
    stats_parser.add_argument("path")
    stats_parser.set_defaults(func=_cmd_stats)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except sqlite3.Error as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
