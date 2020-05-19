from sqlalchemy import create_engine,Column, String, Integer,Float
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

    def __repr__(self):
        return "<User(username='%s')>" % (self.username)


class Threshold(Base):
    __tablename__ = 'threshold'
    id = Column(Integer, primary_key=True)
    threshold = Column(Float)

    def __repr__(self):
        return "<Threshold(threshold='%f')>" % (self.threshold)


# Base.metadata.drop_all()
# Base.metadata.create_all()