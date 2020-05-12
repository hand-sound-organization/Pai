from sqlalchemy import create_engine,Column, String, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///C:\\Users\\asus\\Desktop\\信息安全\\Pai\\DataBase\\PaiDB.db")
Base = declarative_base(engine)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    lockid = Column(String(50))
    token = Column(String(50))
    memberlist = Column(String(50))
    datastart = Column(String(100))
    dataend = Column(String(50))
    datalist = Column(String(150))

    def __repr__(self):
        return "<User(username='%s', password='%s')>" % (self.username,self.password)


# Base.metadata.drop_all()
# Base.metadata.create_all()