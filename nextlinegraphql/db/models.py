from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, Integer, String


Base = declarative_base()


class Hello(Base):
    __tablename__ = "hello"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
