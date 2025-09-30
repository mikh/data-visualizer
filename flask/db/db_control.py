"""Module db_control contains administrative functions for the metadata database."""

from typing import List

import argparse
import os
import sys
import shutil
import json
import subprocess

from sqlalchemy.orm import Session

from db import db_interface


def parse_args(args: List[str]) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Metadata database administration")
    parser.add_argument(
        "--db-path",
        type=str,
        default=os.path.join("untracked", "metadata.sqlite"),
        help="Path to the metadata database.",
    )
    parser.add_argument(
        "--data-file-dir",
        type=str,
        default=os.path.join("untracked", "data"),
        help="Path to the data file directory.",
    )

    subparsers = parser.add_subparsers(dest="subcommand")
    create_parser = subparsers.add_parser("create", help="Create the database.")
    create_parser.add_argument(
        "--delete-existing",
        action="store_true",
        help="Delete the existing database if there is one.",
    )
    create_parser.add_argument(
        "--db-seed-data",
        type=str,
        default="",
        help="Path to the database seed data in JSON format. If empty, database will be empty.",
    )
    create_parser.add_argument(
        "--data-seed-dir",
        type=str,
        default="",
        help=(
            "Path to the data file directory seed data in JSON format. "
            "If empty, data file directory will be empty."
        ),
    )
    create_parser.set_defaults(control="create")

    delete_parser = subparsers.add_parser("delete", help="Delete the database.")
    delete_parser.add_argument(
        "--delete-data-files", action="store_true", help="Delete the data files."
    )
    delete_parser.set_defaults(control="delete")

    migrate_parser = subparsers.add_parser("migrate", help="Migrate the database.")
    migrate_parser.add_argument(
        "--message", type=str, help="Message for the migration."
    )
    migrate_parser.set_defaults(control="migrate")

    export_parser = subparsers.add_parser("export", help="Export the database.")
    export_parser.add_argument(
        "--output-db-file",
        type=str,
        help="Path to the output database file.",
        required=True,
    )
    export_parser.add_argument(
        "--output-data-file-dir",
        type=str,
        help="Path to the output data file directory.",
        required=True,
    )
    export_parser.set_defaults(control="export")

    return parser.parse_args(args)


def create(
    db_path: str,
    data_file_dir: str,
    delete_existing: bool,
    db_seed_data: str,
    data_seed_dir: str,
):
    """Create the database."""
    if delete_existing and os.path.exists(db_path):
        os.remove(db_path)
    if delete_existing and os.path.exists(data_file_dir):
        shutil.rmtree(data_file_dir)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    os.makedirs(data_file_dir, exist_ok=True)
    engine = db_interface.make_engine(db_path)
    if db_seed_data:
        with open(db_seed_data, "r", encoding="utf-8") as file:
            db_seed_data = json.load(file)
        with Session(engine) as session:
            db_interface.mass_add_objects(session, db_seed_data)
    if data_seed_dir:
        shutil.rmtree(data_file_dir)
        shutil.copytree(data_seed_dir, data_file_dir)


def delete_db(db_path: str, data_file_dir: str, delete_data_files: bool):
    """Delete the database."""
    if delete_data_files:
        shutil.rmtree(data_file_dir)
    os.remove(db_path)


def migrate(message: str):
    """Migrate the database."""
    subprocess.check_output(
        ["alembic", "revision", "--autogenerate", "--message", message]
    )
    subprocess.check_output(["alembic", "upgrade", "head"])


def export(
    db_path: str, data_file_dir: str, output_db_file: str, output_data_file_dir: str
):
    """Export the database."""
    engine = db_interface.make_engine(db_path)
    with Session(engine) as session:
        db_objects = db_interface.export_db_objects(session)
    os.makedirs(os.path.dirname(output_db_file), exist_ok=True)
    os.makedirs(os.path.dirname(output_data_file_dir), exist_ok=True)
    with open(output_db_file, "w", encoding="utf-8") as file:
        json.dump(db_objects, file)

    shutil.copytree(data_file_dir, output_data_file_dir)


def main(args: List[str]):
    """Main function."""
    args = parse_args(args)

    match args.control:
        case "create":
            create(
                args.db_path,
                args.data_file_dir,
                args.delete_existing,
                args.db_seed_data,
                args.data_seed_dir,
            )
        case "delete":
            delete_db(args.db_path, args.data_file_dir, args.delete_data_files)
        case "migrate":
            migrate(args.message)
        case "export":
            export(
                args.db_path,
                args.data_file_dir,
                args.output_db_file,
                args.output_data_file_dir,
            )
        case _:
            raise ValueError(f"Invalid control: {args.control}")


if __name__ == "__main__":
    main(sys.argv[1:])
