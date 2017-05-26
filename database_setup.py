import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Category(Base):
    __tablename__ = 'category'
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)

    @property
    def serialize(self):
        #Returns object data in easily serializable format
        return {
            'name': self.name,
            'id': self.id
        }


class Course(Base):
    __tablename__ = 'course'
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(250))
    img_url = Column(String(250))
    intro_video_url = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    @property
    def serialize(self):
        #Returns object data in easily serializable format
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description,
            'img-url': self.img_url
        }


#####EOF#####
engine = create_engine('sqlite:///cs_training.db')

Base.metadata.create_all(engine)