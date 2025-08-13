"""Module db_interface contains functions to interface with metadata database."""

from typing import List

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session

from db.models import Base, Tag


def make_engine(db_path: str) -> Engine:
    """Create a new engine for the database."""
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    return engine


def get_tag_list(engine: Engine) -> List[str]:
    """Get a list of all tags in the database."""
    with Session(engine) as session:
        tags = session.query(Tag).all()
        return [tag.name for tag in tags]
