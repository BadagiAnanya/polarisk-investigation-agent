from __future__ import annotations

import argparse
import json

from .data import CASES, DEFAULT_DB, seed_database
from .engine import evaluate, investigate


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthetic, auditable investigation-agent demo")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("seed", help="Create the local SQLite demo database")
    subparsers.add_parser("list-cases", help="List synthetic investigation cases")
    investigate_parser = subparsers.add_parser("investigate", help="Investigate one alert")
    investigate_parser.add_argument("alert_id")
    subparsers.add_parser("evaluate", help="Run the regression evaluation suite")
    args = parser.parse_args()

    if args.command == "seed":
        print(f"Seeded synthetic data at: {seed_database()}")
    elif args.command == "list-cases":
        print(json.dumps(CASES, indent=2))
    else:
        if not DEFAULT_DB.exists():
            seed_database()
        result = investigate(args.alert_id) if args.command == "investigate" else evaluate()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
