"""Module db_interface contains functions to interface with metadata database."""

from typing import List, Dict, Any, Union

from flask.cli import F
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session

from db.models import Base, Tag, FileMetadata


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


def get_file_list(engine: Engine) -> List[Dict[str, Any]]:
    """Get a list of all files in the database."""
    with Session(engine) as session:
        files = session.query(FileMetadata).all()
        return [file.to_dict() for file in files]


def get_db_object_by_key(
    session: Session, model_name: str, key: str, value: Any
) -> Union[None, FileMetadata, Tag]:
    """Get a database object by key."""
    model = None
    match model_name:
        case "file_metadata":
            model = FileMetadata
        case "tag":
            model = Tag
    if model is None:
        return None
    return session.query(model).filter(getattr(model, key) == value).first()


def create_or_get_file_metadata(
    session: Session, file_metadata: Dict[str, Any]
) -> FileMetadata:
    """Creates FileMetadata object or returns existing one."""
    file_metadata_path = file_metadata["path"]
    file_metadata_object = (
        session.query(FileMetadata)
        .filter(FileMetadata.path == file_metadata_path)
        .first()
    )
    if file_metadata_object is None:
        tags = file_metadata.pop("tags")
        file_metadata_object = FileMetadata(**file_metadata)
        session.add(file_metadata_object)
        session.flush()
        for tag in tags:
            tag = create_or_get_tag(session, tag)
            if tag not in file_metadata_object.tags:
                file_metadata_object.tags.append(tag)
    return file_metadata_object


def create_or_get_tag(session: Session, tag: str) -> Tag:
    """Creates Tag object or returns existing one."""
    tag_object = session.query(Tag).filter(Tag.name == tag).first()
    if tag_object is None:
        tag_object = Tag(name=tag)
        session.add(tag_object)
        session.flush()
    return tag_object


def mass_add_objects(session: Session, objects: Dict[str, List[Dict[str, Any]]]):
    """Adds objects to database."""
    for table_name, table_objects in objects.items():
        for table_object in table_objects:
            match table_name:
                case "file_metadata":
                    create_or_get_file_metadata(session, table_object)
        session.commit()


def export_db_objects(session: Session) -> Dict[str, List[Dict[str, Any]]]:
    """Export database objects to a dictionary."""
    file_metadata = session.query(FileMetadata).all()
    file_metadata = [file_metadata.to_dict() for file_metadata in file_metadata]
    for single_file in file_metadata:
        del single_file["id"]
    return {
        "file_metadata": file_metadata,
    }


def get_object_counts(engine: Engine) -> Dict[str, int]:
    """Get the object counts for all tables in the database."""
    with Session(engine) as session:
        return {
            table.name: session.query(table).count()
            for table in Base.metadata.tables.values()
        }
