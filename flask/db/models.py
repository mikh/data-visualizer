"""Module models contains the models for the metadata database."""

from typing import List, Dict, Any

from sqlalchemy import String, Table, Column, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, relationship

Base = declarative_base()

file_tags = Table(
    "file_tags",
    Base.metadata,
    Column("file_id", Integer, ForeignKey("file_metadata.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.id"), primary_key=True),
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
