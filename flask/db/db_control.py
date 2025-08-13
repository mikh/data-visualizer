"""Module db_control contains administrative functions for the metadata database."""

from typing import List

import argparse
import os
import sys

from db.db_interface import make_engine


def parse_args(args: List[str]) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Metadata database administration")

    parser.add_argument("--init", action="store_true", help="Initialize the database")
    parser.add_argument("--delete", action="store_true", help="Delete database.")
    parser.add_argument("--migrate", action="store_true", help="Migrate the database.")
    parser.add_argument(
        "--db-path",
        type=str,
        default=os.path.join("untracked", "metadata.sqlite"),
        help="Path to the metadata database.",
    )

    return parser.parse_args(args)


def main(args: List[str]):
    """Main function."""
    args = parse_args(args)

    if args.delete:
        os.remove(args.db_path)

    if args.init:
        os.makedirs(os.path.dirname(args.db_path), exist_ok=True)
        make_engine(args.db_path)

    if args.migrate and not args.delete and not args.init:
        raise NotImplementedError("Migration is not implemented yet.")


if __name__ == "__main__":
    main(sys.argv[1:])
