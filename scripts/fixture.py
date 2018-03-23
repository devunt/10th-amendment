import json

from .models import Base, engine
from .models import NewParagraph, NewArticle
from .models import OldParagraph, OldArticle
from .models import article_map_table


def load_fixtures(data):
    data = json.loads(data)

    Base.metadata.create_all(engine)

    engine.execute(OldArticle.__table__.insert(), data['articles']['old_articles'])
    engine.execute(NewArticle.__table__.insert(), data['articles']['new_articles'])

    engine.execute(OldParagraph.__table__.insert(), data['paragraphs']['old_paragraphs'])
    engine.execute(NewParagraph.__table__.insert(), data['paragraphs']['new_paragraphs'])

    engine.execute(article_map_table.insert(), data['article_maps'])
