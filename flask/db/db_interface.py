"""Module db_interface contains functions to interface with metadata database."""

from typing import List, Dict, Any, Union

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session

from db.models import Base, BaseModel, Tag, FileMetadata, FileStats, ColumnStats


def _name_to_model(model_name: str) -> Union["BaseModel", None]:
    """Convert a model name to a model class."""
    match model_name:
        case "file_metadata":
            return FileMetadata
        case "tag":
            return Tag
        case "file_stats":
            return FileStats
        case "column_stats":
            return ColumnStats
        case _:
            return None


def make_engine(db_path: str) -> Engine:
    """Create a new engine for the database."""
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    return engine


def get_all_of_model(
    engine: Engine, model_name: str
) -> Union[None, List[Dict[str, Any]]]:
    """Get all objects of a given model from the database."""
    model = _name_to_model(model_name)
    if model is None:
        return None
    with Session(engine) as session:
        return [object.to_dict() for object in session.query(model).all()]


def get_db_object_by_key(
    session: Session, model_name: str, key: str, value: Any
) -> Union[None, FileMetadata, Tag]:
    """Get a database object by key."""
    model = _name_to_model(model_name)
    if model is None:
        return None
    return session.query(model).filter(getattr(model, key) == value).first()


def create_or_get_object(
    session: Session, model_name: str, data: Dict[str, Any]
) -> Union[None, Any]:
    """Create or get a database object."""
    model = _name_to_model(model_name)
    if model is None:
        return None
    return model.create_or_get(session, data)


def mass_add_objects(session: Session, objects: Dict[str, List[Dict[str, Any]]]):
    """Adds objects to database."""
    for table_name, table_objects in objects.items():
        for table_object in table_objects:
            create_or_get_object(session, table_name, table_object)
        session.commit()


def export_db_objects(
    engine: Engine, export_all: bool = False
) -> Dict[str, List[Dict[str, Any]]]:
    """Export database objects to a dictionary.
    Since file_metadata is the top level object, we only use that to export."""
    objects = {}
    tables = ["file_metadata"]
    if export_all:
        tables = Base.metadata.tables.keys()
    for table_name in tables:
        objects[table_name] = get_all_of_model(engine, table_name)
    return objects


def get_object_counts(engine: Engine) -> Dict[str, int]:
    """Get the object counts for all tables in the database."""
    with Session(engine) as session:
        return {
            table.name: session.query(table).count()
            for table in Base.metadata.tables.values()
        }


def update_object(engine: Engine, model_name: str, new_data: Dict[str, Any]) -> str:
    """Update object in db."""
    with Session(engine) as session:
        model = _name_to_model(model_name)
        if not model:
            return f"Could not find model class with name: '{model_name}'"

        primary_key = model.get_primary_key()
        model_object = model.find_by_primary_key(session, new_data.get(primary_key))
        if not model_object:
            return "Could not find model object."
        model_object.update_object(session, new_data)
        session.commit()
    return ""
