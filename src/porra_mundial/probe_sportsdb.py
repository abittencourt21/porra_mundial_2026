from __future__ import annotations

import argparse
import json

from .sportsdb import fetch_world_cup_events, summarize_payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Sondea TheSportsDB para Mundial 2026.")
    parser.add_argument("--season", default="2026")
    args = parser.parse_args()

    payload = fetch_world_cup_events(args.season)
    print(json.dumps(summarize_payload(payload), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
