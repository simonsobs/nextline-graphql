from typing import Type

from sqlalchemy import Column, Integer, MetaData, Text
from sqlalchemy.orm import DeclarativeBase

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    # "ck": "ck_%(table_name)s_%(constraint_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    metadata = metadata


class Entity(Base):
    __tablename__ = "entity"
    id = Column(Integer, primary_key=True, index=True)
    num = Column(Integer)
    txt = Column(Text)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id!r}, {self.num!r}, {self.txt!r}>"


ModelType = Type[Entity]
