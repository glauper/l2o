from config.config import DBConfig
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, JSON

cfg = DBConfig()
Base = declarative_base()


class Episode(Base):
    __tablename__ = 'episodes'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)  # Optional, if you want to name or otherwise identify episodes
    state_trajectories = Column(JSON)  # Store state trajectories as JSON
    epochs = relationship("Epoch", backref="episode")

class Epoch(Base):
    __tablename__ = 'epochs'
    
    id = Column(Integer, primary_key=True)
    episode_id = Column(Integer, ForeignKey('episodes.id'))
    time_step = Column(Integer, nullable=False)
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    image = Column(String, nullable=False)  # Store images as binary data


engine = create_engine(f'sqlite:///{cfg.db_name}')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)