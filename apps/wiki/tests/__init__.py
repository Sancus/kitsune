from django.template.defaultfilters import slugify
from django.core.cache import cache

from datetime import datetime

from sumo.tests import LocalizingClient, TestCase, get_user
from wiki.models import Document, Revision, CATEGORIES, SIGNIFICANCES


class TestCaseBase(TestCase):
    """Base TestCase for the wiki app test cases."""

    def setUp(self):
        self.client = LocalizingClient()
        cache.clear()

    def tearDown(self):
        pass


def document(**kwargs):
    """Return an empty document with enough stuff filled out that it can be
    saved."""
    defaults = {'category': CATEGORIES[0][0], 'title': str(datetime.now())}
    defaults.update(kwargs)
    if 'slug' not in kwargs:
        defaults['slug'] = slugify(defaults['title'])
    return Document(**defaults)


def revision(**kwargs):
    """Return an empty revision with enough stuff filled out that it can be
    saved.

    Requires a users fixture if no creator is provided.

    """
    u = None
    if 'creator' not in kwargs:
        u = get_user()

    d = None
    if 'document' not in kwargs:
        d = document()
        d.save()

    defaults = {'summary': 'Some summary', 'content': 'Some content',
                'significance': SIGNIFICANCES[0][0], 'comment': 'Some comment',
                'creator': u, 'document': d}

    defaults.update(kwargs)

    return Revision(**defaults)


def doc_rev(content=''):
    """Helper creates a document and revision given html and content."""
    d = document()
    d.save()
    r = revision(document=d, content=content, is_approved=True)
    r.save()
    return d, r