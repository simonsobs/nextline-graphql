from sqlalchemy import MetaData, Column, Integer
from sqlalchemy.ext.declarative import declarative_base

from typing import Type


convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    # "ck": "ck_%(table_name)s_%(constraint_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=convention)

Base = declarative_base(metadata=metadata)


class Entity(Base):
    __tablename__ = "entity"
    id = Column(Integer, primary_key=True, index=True)
    num = Column(Integer)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id!r}, {self.num!r}>"


ModelType = Type[Entity]
