from sqlalchemy import create_engine
from sqlalchemy import Table, Column
from sqlalchemy import Integer, String, Text
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# engine = create_engine('mysql+mysqldb://user:password@127.0.0.1:3306/dbname')
engine = create_engine('sqlite:///db.sqlite3')
Base = declarative_base()
Session = sessionmaker(bind=engine)

article_map_table = Table('article_map', Base.metadata,
    Column('old_article_id', Integer, ForeignKey('article_old.id'), primary_key=True),
    Column('new_article_id', Integer, ForeignKey('article_new.id'), primary_key=True),
)


class OldArticle(Base):
    __tablename__ = 'article_old'
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    mapped_into = relationship('NewArticle', secondary=article_map_table, back_populates='mapped_from')
    paragraphs = relationship('OldParagraph', backref='starts_from', lazy=True)


class NewArticle(Base):
    __tablename__ = 'article_new'
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    mapped_from = relationship('OldArticle', secondary=article_map_table, back_populates='mapped_into')
    paragraphs = relationship('NewParagraph', backref='starts_from', lazy=True)


class OldParagraph(Base):
    __tablename__ = 'paragraph_old'
    id = Column(Integer, primary_key=True)
    level = Column(Integer, nullable=False)
    name = Column(String(32), nullable=False)
    starts_from_id = Column(Integer, ForeignKey('article_old.id'), nullable=False)


class NewParagraph(Base):
    __tablename__ = 'paragraph_new'
    id = Column(Integer, primary_key=True)
    level = Column(Integer, nullable=False)
    name = Column(String(32), nullable=False)
    starts_from_id = Column(Integer, ForeignKey('article_new.id'), nullable=False)
