import sqlalchemy
from sqlalchemy.sql.sqltypes import String
from database import Base
from sqlalchemy import Column, String

class User(Base) :
    __tablename__ = 'users'
    username = Column(String(length=20), primary_key=True)
    password = Column(String(length=100))
