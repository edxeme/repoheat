"""Command-line interface for repoheat."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path

from repoheat.churn import FileChurn
from repoheat.gitlog import Commit, GitHistoryError, collect_history
from repoheat.hotspots import BusFactor, Hotspot, bus_factor, hotspots


def _jsonify(rows: list) -> list[dict]:
    """Dataclasses → JSON-safe dicts (datetimes as ISO strings)."""
    out = []
    for row in rows:
        data = asdict(row)
        for key, value in data.items():
            if isinstance(value, (datetime, date)):
                data[key] = value.date().isoformat()
        out.append(data)
    return out


def _print_churn(rows: list[FileChurn]) -> None:
    header = f"{'path':<40} {'commits':>7} {'add':>6} {'del':>6} {'total':>6} {'last':>11}"
    print(header)
    print("-" * len(header))
    for row in rows:
        print(
            f"{row.path:<40} {row.commits:>7} {row.added:>6} {row.deleted:>6} "
            f"{row.total:>6} {row.last_touched.date().isoformat():>11}"
        )


def _print_hotspots(rows: list[Hotspot]) -> None:
    header = f"{'score':>7} {'churn':>6} {'size':>6}  {'path'}"
    print(header)
    print("-" * len(header))
    for row in rows:
        print(f"{row.score:>7} {row.churn:>6} {row.size:>6}  {row.path}")


def _print_bus_factor(rows: list[BusFactor]) -> None:
    header = f"{'authors':>7} {'commits':>7} {'main author':<24} {'path'}"
    print(header)
    print("-" * len(header))
    for row in rows:
        print(f"{row.authors:>7} {row.commits:>7} {row.main_author:<24} {row.path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="repoheat",
        description="Forensics for git repositories: churn, hotspots and bus factor.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_churn = sub.add_parser("churn", help="per-file change volume, heaviest first")
    p_churn.add_argument("path", help="repository root")
    p_churn.add_argument("--since", default=None, help="YYYY-MM-DD, inclusive")
    p_churn.add_argument("--json", action="store_true")

    p_hot = sub.add_parser("hotspots", help="rank files by churn x current size")
    p_hot.add_argument("path", help="repository root")
    p_hot.add_argument("-n", "--top", type=int, default=10)
    p_hot.add_argument("--json", action="store_true")

    p_bus = sub.add_parser("bus-factor", help="files by knowledge concentration")
    p_bus.add_argument("path", help="repository root")
    p_bus.add_argument("-n", "--top", type=int, default=10)
    p_bus.add_argument("--json", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    root = Path(args.path)
    history: list[Commit]
    try:
        history = collect_history(root)
    except GitHistoryError as exc:
        print(f"repoheat: {exc}", file=sys.stderr)
        return 1

    if args.command == "churn":
        from repoheat.churn import aggregate

        rows = aggregate(history, since=args.since)
        if args.json:
            print(json.dumps(_jsonify(rows), indent=2))
        else:
            _print_churn(rows)
    elif args.command == "hotspots":
        rows = hotspots(root, history, top=args.top)
        if args.json:
            print(json.dumps(_jsonify(rows), indent=2))
        else:
            _print_hotspots(rows)
    else:  # bus-factor
        rows = bus_factor(history, top=args.top)
        if args.json:
            print(json.dumps(_jsonify(rows), indent=2))
        else:
            _print_bus_factor(rows)
    return 0
