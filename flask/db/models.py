"""Module models contains the models for the metadata database."""

from typing import List, Dict, Any

from sqlalchemy import String, Table, Column, Integer, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, relationship

Base = declarative_base()

file_tags = Table(
    "file_tags",
    Base.metadata,
    Column("file_id", Integer, ForeignKey("file_metadata.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.id"), primary_key=True),
)

file_column_stats = Table(
    "file_column_stats",
    Base.metadata,
    Column("file_stats_id", Integer, ForeignKey("file_stats.id"), primary_key=True),
    Column("column_stats_id", Integer, ForeignKey("column_stats.id"), primary_key=True),
)


class FileMetadata(Base):  # pylint: disable=too-few-public-methods
    """Model for file metadata."""

    __tablename__ = "file_metadata"

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
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "data_file_type": self.data_file_type,
            "data_file_path": self.data_file_path,
            "tags": self.get_tags(),
        }

    def get_tags(self) -> List[str]:
        """Get the tags for the file metadata."""
        return [tag.name for tag in self.tags]


class Tag(Base):  # pylint: disable=too-few-public-methods
    """Tag Model."""

    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    file_metadata: Mapped[List["FileMetadata"]] = relationship(
        "FileMetadata",
        secondary="file_tags",
        back_populates="tags",
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the tag to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
        }


class FileStats(Base):  # pylint: disable=too-few-public-methods
    """File Stats Model.
    This model is used to store the statistics for a given file.
    """

    __tablename__ = "file_stats"

    id: Mapped[int] = mapped_column(primary_key=True)

    num_columns: Mapped[int] = mapped_column(Integer, nullable=False)
    num_rows: Mapped[int] = mapped_column(Integer, nullable=False)

    column_stats: Mapped[List["ColumnStats"]] = relationship(
        "ColumnStats",
        secondary="file_column_stats",
        back_populates="file_stats",
    )


class ColumnStats(Base):  # pylint: disable=too-few-public-methods
    """Column stats model."""

    __tablename__ = "column_stats"

    id: Mapped[int] = mapped_column(primary_key=True)
    column_name: Mapped[str] = mapped_column(String, nullable=False)
    data_type: Mapped[str] = mapped_column(String, nullable=False)
    num_rows: Mapped[int] = mapped_column(Integer, nullable=False)
    num_unique_values: Mapped[int] = mapped_column(Integer, nullable=False)
    num_null_values: Mapped[int] = mapped_column(Integer, nullable=False)

    # Numeric stats
    num_zeros_values: Mapped[int] = mapped_column(Integer, nullable=False)
    std_dev: Mapped[float] = mapped_column(Float, nullable=False)
    mean: Mapped[float] = mapped_column(Float, nullable=False)
    median: Mapped[float] = mapped_column(Float, nullable=False)
    min_value: Mapped[float] = mapped_column(Float, nullable=False)
    max_value: Mapped[float] = mapped_column(Float, nullable=False)

    # Categorical stats
    num_empty_values: Mapped[int] = mapped_column(Integer, nullable=False)

    file_stats: Mapped["FileStats"] = relationship(
        "FileStats",
        secondary="file_column_stats",
        back_populates="column_stats",
    )
