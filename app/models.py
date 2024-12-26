from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, func, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression

from database import Base


class Template(Base):
    __tablename__ = "template"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    object_type_id = Column(Integer, nullable=False)
    creation_date = Column(DateTime, server_default=func.now())
    modification_date = Column(DateTime, onupdate=func.now())
    version = Column(Integer, default=1)
    valid: Mapped[bool] = mapped_column(default=True, server_default=expression.true(), nullable=False)

    # Relationships
    template_objects = relationship(
        "TemplateObject",
        back_populates="template",
        cascade="all, delete-orphan"
    )


class TemplateObject(Base):
    __tablename__ = "template_object"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(
        Integer,
        ForeignKey(
            column="template.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )
    parent_object_id = Column(
        Integer,
        ForeignKey("template_object.id"),
        nullable=True
    )
    object_type_id = Column(Integer, nullable=False)
    required = Column(Boolean, default=True, nullable=False)
    valid: Mapped[bool] = mapped_column(default=True, server_default=expression.true(), nullable=False)

    # Relationships
    template = relationship(
        "Template",
        back_populates="template_objects"
    )
    parameters = relationship(
        "TemplateParameter",
        back_populates="template_object",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint(
            "template_id",
            "object_type_id",
            name="uq_template_object"
        ),
        CheckConstraint(
            "id != parent_object_id",
            name="check_parent_object"
        ),
    )


class TemplateParameter(Base):
    __tablename__ = "template_parameter"

    id = Column(Integer, primary_key=True, index=True)
    template_object_id = Column(
        Integer,
        ForeignKey(
            "template_object.id",
            ondelete="CASCADE"
            ),
        nullable=False
    )
    parameter_type_id = Column(Integer, nullable=False)
    value = Column(String, nullable=True)
    constraint = Column(String, nullable=True)
    required = Column(Boolean, default=False, nullable=False)
    val_type: Mapped[str] = mapped_column(nullable=False)
    valid: Mapped[bool] = mapped_column(default=True, server_default=expression.true(), nullable=False)

    # Relationships
    template_object = relationship(
        "TemplateObject",
        back_populates="parameters"
    )
