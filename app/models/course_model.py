from app.database import Base

from category_model import Category

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Course(Base):
    __tablename__ = 'course'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    img_url = Column(String(250))
    intro_video_url = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    @property
    def serialize(self):
        # Return object data in easily serializable format
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description,
            'img-url': self.img_url
        }