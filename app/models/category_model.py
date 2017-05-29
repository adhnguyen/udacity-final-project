from app.database import Base

from sqlalchemy import Column, Integer, String


class Category(Base):
    __tablename__ = 'category'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)

    @property
    def serialize(self):
        # Return object data in easily serializable format
        return {
            'name': self.name,
            'id': self.id
        }
