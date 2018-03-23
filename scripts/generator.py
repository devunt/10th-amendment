import json
from difflib import SequenceMatcher

from .models import NewParagraph, NewArticle
from .models import OldParagraph, OldArticle
from .models import Session


def generate_data_json():
    articles_pairs = []

    session = Session()

    all_old_articles = session.query(OldArticle).order_by(OldArticle.id).all()
    all_new_articles = session.query(NewArticle).order_by(NewArticle.id).all()

    for old_article in all_old_articles:
        articles_pair = {
            'old_articles': [old_article.id],
            'new_articles': [],
        }

        append = True
        for mapped_new_article in old_article.mapped_into:
            articles_pair['new_articles'].append(mapped_new_article.id)
            if len(mapped_new_article.mapped_from) > 1:
                if old_article.id == mapped_new_article.mapped_from[0].id:
                    articles_pair['old_articles'] += map(lambda x: x.id, mapped_new_article.mapped_from[1:])
                else:
                    append = False
                    break

        if append:
            articles_pairs.append(articles_pair)

    for new_article in all_new_articles:
        mapped_count = len(new_article.mapped_from)
        if mapped_count == 0:
            articles_pairs.append({
                'old_articles': [],
                'new_articles': [new_article.id],
            })

    def sorting(x):
        if len(x['new_articles']) > 0:
            return x['new_articles'][0]
        if len(x['old_articles']) > 0:
            return x['old_articles'][0]
        return 0
    articles_pairs = sorted(articles_pairs, key=sorting)

    def get_paragraphs(old_attached_paragraphs, new_attached_paragraphs):
        old_attached_paragraph_name_set = {p.name for p in old_attached_paragraphs}
        new_attached_paragraph_name_set = {p.name for p in new_attached_paragraphs}

        old_paragraph_name_set = old_attached_paragraph_name_set - new_attached_paragraph_name_set
        new_paragraph_name_set = new_attached_paragraph_name_set - old_attached_paragraph_name_set
        paragraph_name_set = old_attached_paragraph_name_set & new_attached_paragraph_name_set

        def pd(model, names):
            return sorted([{'id': p.id, 'level': p.level, 'name': p.name} for p in map(lambda x: session.query(model).filter_by(name=x).first(), names)], key=lambda x: x['id'])

        return {
            'old_paragraphs': pd(OldParagraph, old_paragraph_name_set),
            'new_paragraphs': pd(NewParagraph, new_paragraph_name_set),
            'paragraphs': pd(NewParagraph, paragraph_name_set),
        }

    changesets = []
    for articles_pair in articles_pairs:
        old_article_count = len(articles_pair['old_articles'])
        new_article_count = len(articles_pair['new_articles'])
        
        old_articles = list(map(lambda x: all_old_articles[x - 1], articles_pair['old_articles']))
        new_articles = list(map(lambda x: all_new_articles[x - 1], articles_pair['new_articles']))

        if old_article_count == 1 and new_article_count == 1:
            old_source = old_articles[0].text.replace('\n', ' \n').split(' ')
            new_source = new_articles[0].text.replace('\n', ' \n').split(' ')

            old_diff = []
            new_diff = []

            matcher = SequenceMatcher(None, old_source, new_source)
            for tag, alo, ahi, blo, bhi in matcher.get_opcodes():
                old_phrase = ' '.join(old_source[alo:ahi]).replace(' \n', '\n')
                new_phrase = ' '.join(new_source[blo:bhi]).replace(' \n', '\n')

                if tag == 'replace':
                    old_diff.append({'status': 'deleted', 'phrase': old_phrase})
                    new_diff.append({'status': 'added', 'phrase': new_phrase})
                elif tag == 'delete':
                    old_diff.append({'status': 'deleted', 'phrase': old_phrase})
                elif tag == 'insert':
                    new_diff.append({'status': 'added', 'phrase': new_phrase})
                elif tag == 'equal':
                    old_diff.append({'status': 'unchanged', 'phrase': old_phrase})
                    new_diff.append({'status': 'unchanged', 'phrase': new_phrase})

            changeset = {
                'old_articles': [{'id': old_articles[0].id, 'diffs': old_diff}],
                'new_articles': [{'id': new_articles[0].id, 'diffs': new_diff}],
            }
            changeset.update(get_paragraphs(old_articles[0].paragraphs, new_articles[0].paragraphs))
        else:
            changeset = {
                'old_articles': [],
                'new_articles': [],
            }

            old_attached_paragraphs = []
            new_attached_paragraphs = []

            for old_article in old_articles:
                changeset['old_articles'].append({'id': old_article.id, 'diffs': [{'status': 'deleted', 'phrase': old_article.text}]})
                old_attached_paragraphs += old_article.paragraphs

            for new_article in new_articles:
                changeset['new_articles'].append({'id': new_article.id, 'diffs': [{'status': 'deleted', 'phrase': new_article.text}]})
                new_attached_paragraphs += new_article.paragraphs

            changeset.update(get_paragraphs(old_attached_paragraphs, new_attached_paragraphs))

        if old_article_count == 0 and new_article_count > 0:
            changeset['status'] = 'added'
        elif old_article_count > 0 and new_article_count == 0:
            changeset['status'] = 'deleted'
        elif old_article_count > 0 and new_article_count > 0:
            changeset['status'] = 'changed'

        changesets.append(changeset)

    return json.dumps({'changesets': changesets})
