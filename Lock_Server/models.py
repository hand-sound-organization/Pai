from sqlalchemy import create_engine, Column, String, Integer
from Lock_Server.dbconfig import Base


class User(Base):
    id = Column(Integer,primary_key=True)
    username = Column(String(50))
    password = Column(String(50))

    def __repr__(self):
        return "<User(username='%s', password='%s')>" % (self.username,self.password)


Base.metadata.drop_all()
Base.metadata.create_all()