#!/usr/bin/env python3
"""Create a new rust-embedded/wg meeting minutes discussion on GitHub."""

import argparse
import json
import subprocess
import sys
from datetime import date, timedelta


REPO_ID = "MDEwOlJlcG9zaXRvcnk2OTUyMDc2NQ=="
CATEGORY_ID = "DIC_kwDOBCTNfc4CelXZ"  # General


def next_tuesday(from_date: date) -> date:
    """Return the next Tuesday on or after from_date."""
    days_ahead = (1 - from_date.weekday()) % 7  # Tuesday = weekday 1
    return from_date + timedelta(days=days_ahead)


def make_body(meeting_date: date) -> str:
    date_str = meeting_date.strftime("%Y-%m-%d")
    return (
        "This is the agenda for the next meeting. "
        "Please add anything you'd like to discuss below!\r\n"
        "\r\n"
        "*  Meetings: Tuesday 8pm Europe/Berlin time\r\n"
        "*  [Join the Matrix chat](https://matrix.to/#/#rust-embedded:matrix.org)\r\n"
        f"*  [IRC/Matrix logs](https://libera.irclog.whitequark.org/rust-embedded/{date_str})"
    )


def create_discussion(meeting_date: date, dry_run: bool) -> None:
    date_str = meeting_date.strftime("%Y-%m-%d")
    title = f"Meeting {date_str}"
    body = make_body(meeting_date)

    if dry_run:
        print(f"Title: {title}")
        print(f"Body:\n{body}")
        return

    mutation = """
    mutation($repoId: ID!, $categoryId: ID!, $title: String!, $body: String!) {
      createDiscussion(input: {
        repositoryId: $repoId
        categoryId: $categoryId
        title: $title
        body: $body
      }) {
        discussion {
          url
          number
        }
      }
    }
    """

    result = subprocess.run(
        [
            "gh", "api", "graphql",
            "-f", f"query={mutation}",
            "-f", f"repoId={REPO_ID}",
            "-f", f"categoryId={CATEGORY_ID}",
            "-f", f"title={title}",
            "-f", f"body={body}",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(result.stdout)
    if "errors" in data:
        print(f"GraphQL errors: {data['errors']}", file=sys.stderr)
        sys.exit(1)

    discussion = data["data"]["createDiscussion"]["discussion"]
    print(f"Created discussion #{discussion['number']}: {discussion['url']}")


def main():
    parser = argparse.ArgumentParser(
        description="Create a rust-embedded/wg meeting minutes discussion."
    )
    parser.add_argument(
        "date",
        nargs="?",
        help="Meeting date as YYYY-MM-DD (default: next Tuesday)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the title and body without creating the discussion",
    )
    args = parser.parse_args()

    if args.date:
        try:
            meeting_date = date.fromisoformat(args.date)
        except ValueError:
            print(f"Invalid date: {args.date!r} (expected YYYY-MM-DD)", file=sys.stderr)
            sys.exit(1)
    else:
        meeting_date = next_tuesday(date.today())

    create_discussion(meeting_date, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
