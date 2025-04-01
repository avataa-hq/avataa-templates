from sqlalchemy import MetaData
from sqlalchemy.orm import (
    DeclarativeBase,
    MappedAsDataclass,
)

convention = {
    "ix": "ix_%(column_0_label)s",  # INDEX
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",  # UNIQUE
    "ck": "ck_%(table_name)s_%(constraint_name)s",  # CHECK
    "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",  # FOREIGN KEY
    "pk": "pk_%(table_name)s",  # PRIMARY KEY
}


class Base(DeclarativeBase, MappedAsDataclass):
    metadata = MetaData(naming_convention=convention)
