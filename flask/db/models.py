"""Module models contains the models for the metadata database."""

from typing import List, Dict, Any, Union

from sqlalchemy import String, Table, Column, Integer, ForeignKey, Float
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    declarative_base,
    relationship,
    Session,
)

Base = declarative_base()

file_tags = Table(
    "file_tags",
    Base.metadata,
    Column("file_id", Integer, ForeignKey("file_metadata.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.id"), primary_key=True),
)


class BaseModel(Base):
    """Base model for all models."""

    __abstract__ = True
    _primary_key: str = None

    @classmethod
    def get_primary_key(cls) -> str:
        """Get the primary key for the model."""
        return cls._primary_key

    @classmethod
    def find_by_key(
        cls, session: Session, key: str, value: Any
    ) -> Union[None, "BaseModel"]:
        """Find a model object by key."""
        return session.query(cls).filter(getattr(cls, key) == value).first()

    @classmethod
    def find_by_primary_key(
        cls, session: Session, value: Any
    ) -> Union[None, "BaseModel"]:
        """Find a model object by primary key."""
        return cls.find_by_key(session, cls.get_primary_key(), value)

    @classmethod
    def create_new(cls, session: Session, data: Dict[str, Any]) -> "BaseModel":
        """Create a new model object."""
        obj = cls(**data)
        session.add(obj)
        session.flush()
        return obj

    @classmethod
    def create_or_get(
        cls, session: Session, data: Dict[str, Any]
    ) -> Union[None, "BaseModel"]:
        """Create or get a model object."""
        value = data.get(cls.get_primary_key(), None)
        if value is None:
            return None  # pragma: no cover
        obj = cls.find_by_primary_key(session, value)
        if obj is None:
            obj = cls.create_new(session, data)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        """Convert the model object to a dictionary."""
        columns = [
            column.name for column in self.__table__.columns if column.name != "id"
        ]
        return {column: getattr(self, column) for column in columns}

    def update_object(self, session: Session, new_data: Dict[str, Any]):
        """Update object with new data."""
        for key, value in new_data.items():
            setattr(self, key, value)
        session.flush()


class FileMetadata(BaseModel):  # pylint: disable=too-few-public-methods
    """Model for file metadata."""

    __tablename__ = "file_metadata"
    _primary_key = "path"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)
    data_file_type: Mapped[str] = mapped_column(String, nullable=False)
    data_file_path: Mapped[str] = mapped_column(String, nullable=False)

    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary="file_tags",
        back_populates="file_metadata",
    )

    file_stats: Mapped["FileStats"] = relationship(
        "FileStats",
        back_populates="file_metadata",
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the file metadata to a dictionary."""
        return {
            "name": self.name,
            "path": self.path,
            "data_file_type": self.data_file_type,
            "data_file_path": self.data_file_path,
            "tags": self.get_tags(),
            "file_stats": self.file_stats.to_dict() if self.file_stats else None,
        }

    def get_tags(self) -> List[str]:
        """Get the tags for the file metadata."""
        return [tag.name for tag in self.tags]

    @classmethod
    def create_new(cls, session: Session, data: Dict[str, Any]) -> "FileMetadata":
        """Create a new file metadata object."""
        tags = data.pop("tags", [])
        file_stats = data.pop("file_stats", {})
        file_metadata_object = cls(**data)
        session.add(file_metadata_object)
        session.flush()
        for tag in tags:
            tag_object = Tag.create_or_get(session, {"name": tag})
            if tag_object not in file_metadata_object.tags:
                file_metadata_object.tags.append(tag_object)
        if file_stats:
            file_stats_object = FileStats.create_new(session, file_stats)
            file_metadata_object.file_stats = file_stats_object
        return file_metadata_object

    def update_object(self, session: Session, new_data: Dict[str, Any]):
        tags = new_data.pop("tags", None)
        file_stats = new_data.pop("file_stats", None)
        super().update_object(session, new_data)

        if tags is not None:
            new_tags = []
            for tag in tags:
                tag_object = Tag.create_or_get(session, {"name": tag})
                new_tags.append(tag_object)
            self.tags = new_tags

        if file_stats is not None:
            if self.file_stats:
                self.file_stats.update_object(session, file_stats)
            else:
                file_stats_object = FileStats.create_new(session, file_stats)
                self.file_stats = file_stats_object


class Tag(BaseModel):  # pylint: disable=too-few-public-methods
    """Tag Model."""

    __tablename__ = "tag"
    _primary_key = "name"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    file_metadata: Mapped[List["FileMetadata"]] = relationship(
        "FileMetadata",
        secondary="file_tags",
        back_populates="tags",
    )


class FileStats(BaseModel):  # pylint: disable=too-few-public-methods
    """File Stats Model.
    This model is used to store the statistics for a given file.
    """

    __tablename__ = "file_stats"
    _primary_key = "path"

    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(String, nullable=False)
    file_metadata_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("file_metadata.id"), unique=True, nullable=True
    )

    num_columns: Mapped[int] = mapped_column(Integer, nullable=False)
    num_rows: Mapped[int] = mapped_column(Integer, nullable=False)

    file_metadata: Mapped["FileMetadata"] = relationship(
        "FileMetadata",
        back_populates="file_stats",
    )

    column_stats: Mapped[List["ColumnStats"]] = relationship(
        "ColumnStats",
        back_populates="file_stats",
    )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the file stats to a dictionary."""
        return {
            "path": self.path,
            "num_columns": self.num_columns,
            "num_rows": self.num_rows,
            "column_stats": [
                column_stat.to_dict() for column_stat in self.column_stats
            ],
        }

    @classmethod
    def create_new(cls, session: Session, data: Dict[str, Any]) -> "FileStats":
        """Create a new file stats object."""
        column_stats = data.pop("column_stats", [])
        file_stats_object = cls(**data)
        session.add(file_stats_object)
        session.flush()
        for column_stat in column_stats:
            column_stat_object = ColumnStats.create_new(session, column_stat)
            if column_stat_object not in file_stats_object.column_stats:
                file_stats_object.column_stats.append(column_stat_object)
        return file_stats_object

    def find_column(self, column_name: str) -> Union["ColumnStats", None]:
        """Find a ColumnStats object by column name."""
        if self.column_stats:
            for column in self.column_stats:
                if column.column_name == column_name:
                    return column
        return None

    def update_object(self, session: Session, new_data: Dict[str, Any]):
        column_stats = new_data.pop("column_stats", None)
        super().update_object(session, new_data)

        if column_stats is not None:
            new_column_stats = []
            for column in column_stats:
                existing_column = self.find_column(column.get("column_name"))
                if existing_column:
                    existing_column.update_object(session, column)
                    new_column_stats.append(existing_column)
                else:
                    new_column_stats.append(ColumnStats.create_new(session, column))
            self.column_stats = new_column_stats


class ColumnStats(BaseModel):  # pylint: disable=too-few-public-methods
    """Column stats model."""

    __tablename__ = "column_stats"
    _primary_key = "column_name"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_stats_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("file_stats.id"), nullable=True
    )
    column_name: Mapped[str] = mapped_column(String, nullable=False)
    data_type: Mapped[str] = mapped_column(String, nullable=False)
    num_rows: Mapped[int] = mapped_column(Integer, nullable=False)
    num_unique_values: Mapped[int] = mapped_column(Integer, nullable=False)
    num_null_values: Mapped[int] = mapped_column(Integer, nullable=False)

    # Numeric stats
    num_zeros_values: Mapped[int] = mapped_column(Integer, default=0)
    std_dev: Mapped[float] = mapped_column(Float, default=0.0)
    mean: Mapped[float] = mapped_column(Float, default=0.0)
    median: Mapped[float] = mapped_column(Float, default=0.0)
    min_value: Mapped[float] = mapped_column(Float, default=0.0)
    max_value: Mapped[float] = mapped_column(Float, default=0.0)

    # Categorical stats
    num_empty_values: Mapped[int] = mapped_column(Integer, default=0)

    file_stats: Mapped["FileStats"] = relationship(
        "FileStats",
        back_populates="column_stats",
    )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the column stats to a dictionary."""
        output = super().to_dict()
        output.pop("file_stats_id")
        return output
