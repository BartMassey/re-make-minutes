#!/usr/bin/env python3
"""Create a new rust-embedded/wg meeting minutes discussion on GitHub."""

import argparse
import json
import subprocess
import sys
from datetime import date, timedelta


REPO_OWNER = "rust-embedded"
REPO_NAME = "wg"
CATEGORY_NAME = "General"


def lookup_repo_and_category() -> tuple[str, str]:
    """Return (repo_id, category_id) by querying the GitHub API."""
    query = """
    query($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        id
        discussionCategories(first: 25) {
          nodes { id name }
        }
      }
    }
    """
    result = subprocess.run(
        [
            "gh", "api", "graphql",
            "-f", f"query={query}",
            "-f", f"owner={REPO_OWNER}",
            "-f", f"name={REPO_NAME}",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Error looking up repo: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(result.stdout)
    if "errors" in data:
        print(f"GraphQL errors: {data['errors']}", file=sys.stderr)
        sys.exit(1)

    repo = data["data"]["repository"]
    repo_id = repo["id"]

    categories = repo["discussionCategories"]["nodes"]
    matches = [c for c in categories if c["name"] == CATEGORY_NAME]
    if not matches:
        names = [c["name"] for c in categories]
        print(
            f"Category {CATEGORY_NAME!r} not found. Available: {names}",
            file=sys.stderr,
        )
        sys.exit(1)

    return repo_id, matches[0]["id"]


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

    repo_id, category_id = lookup_repo_and_category()

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
            "-f", f"repoId={repo_id}",
            "-f", f"categoryId={category_id}",
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
