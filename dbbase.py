from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine


Base = declarative_base()


class Car(Base):
    __tablename__ = 'car_circulate'
    id = Column(Integer, primary_key=True, autoincrement=True)
    license = Column(String(30), nullable=False)
    type = Column(String(10), nullable=False)
    in_time = Column(String(30), nullable=False)
    out_time = Column(String(30))


engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/test?charset=utf8')
Base.metadata.create_all(engine)