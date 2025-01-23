import datetime

from sqlalchemy import (
    ForeignKey,
    func,
    CheckConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.sql import expression

from database import Base


class Template(Base):
    __tablename__ = "template"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, init=False)
    name: Mapped[str] = mapped_column(nullable=False)
    owner: Mapped[str] = mapped_column(nullable=False)
    object_type_id: Mapped[int] = mapped_column(nullable=False)

    creation_date: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now(),
        server_default=func.now(),
    )
    modification_date: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now(),
        server_default=func.now(),
    )
    valid: Mapped[bool] = mapped_column(
        default=True,
        server_default=expression.true(),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(default=1, server_default="1")

    # Relationships
    template_objects: Mapped[list["TemplateObject"]] = relationship(
        "TemplateObject",
        default_factory=list,
        back_populates="template",
        cascade="all, delete-orphan",
    )


class TemplateObject(Base):
    __tablename__ = "template_object"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, init=False)
    template_id: Mapped[int] = mapped_column(
        ForeignKey(
            column="template.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    parent_object_id: Mapped[int] = mapped_column(
        ForeignKey(
            column="template_object.id",
            ondelete="CASCADE",
        ),
        nullable=True,
    )
    object_type_id: Mapped[int] = mapped_column(nullable=False)

    # Relationships
    template = relationship(
        "Template",
        back_populates="template_objects",
        uselist=False,
    )
    parameters: Mapped[list["TemplateParameter"]] = relationship(
        "TemplateParameter",
        back_populates="template_object",
        cascade="all, delete-orphan",
        default_factory=list,
    )
    required: Mapped[bool] = mapped_column(default=True, nullable=False)
    valid: Mapped[bool] = mapped_column(
        default=True,
        server_default=expression.true(),
        nullable=False,
    )

    __table_args__ = (
        # UniqueConstraint(
        #     "template_id",
        #     "object_type_id",
        #     name="uq_template_object"
        # ),
        CheckConstraint(
            "id != parent_object_id",
            name="check_parent_object",
        ),
    )


class TemplateParameter(Base):
    __tablename__ = "template_parameter"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, init=False)
    template_object_id: Mapped[int] = mapped_column(
        ForeignKey(
            "template_object.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    parameter_type_id: Mapped[int] = mapped_column(nullable=False)
    value: Mapped[str] = mapped_column(nullable=True)
    constraint: Mapped[str] = mapped_column(nullable=True)
    val_type: Mapped[str] = mapped_column(nullable=False)

    # Relationships
    template_object = relationship(
        "TemplateObject",
        back_populates="parameters",
        uselist=False,
    )
    required: Mapped[bool] = mapped_column(default=False, nullable=False)
    valid: Mapped[bool] = mapped_column(
        default=True,
        server_default=expression.true(),
        nullable=False,
    )
