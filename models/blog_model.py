import datetime

from slugify import slugify
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import Session

from database.engine import Base


class Blog(Base):
    __tablename__ = "blogs"
    id: int = Column(Integer, primary_key=True, index=True)
    title: str = Column(String(255), index=True)
    slug: str = Column(String, unique=True, index=True)
    content: str = Column(String())
    updated_at: DateTime = Column(DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    created_at: DateTime = Column(DateTime(), default=datetime.datetime.utcnow)

    @hybrid_method
    def generate_slug(self):
        from slugify import slugify
        return slugify(self.title)

    def __repr__(self) -> str:
        return f"Blog(id={self.id!r}, title={self.title!r}, content={self.content!r})"


def create_slug(db: Session, title: str) -> str:
    try:
        base_slug = slugify(title)
        print(f"Base slug: {base_slug}")

        counter = 1
        while True:
            slug = base_slug if counter == 1 else f"{base_slug}-{counter}"
            if not db.query(Blog).filter(Blog.slug == slug).first():
                return slug
            counter += 1
    except Exception as e:
        print(f"Error in create_slug: {e}")
        raise
