from datetime import datetime

from django.conf import settings
from django.template.defaultfilters import slugify

from nose.tools import eq_

from questions.models import Question
from sumo.tests import LocalizingClient, TestCase


class TestCaseBase(TestCase):
    """Base TestCase for the Questions app test cases."""

    fixtures = ['users.json', 'questions.json']
    client_class = LocalizingClient

    def setUp(self):
        q = Question.objects.get(pk=1)
        q.last_answer_id = 1
        q.save()

        # create a new cache key for top contributors to avoid conflict
        # TODO: May be able to go away once we flush memcache between tests.
        self.orig_tc_cache_key = settings.TOP_CONTRIBUTORS_CACHE_KEY
        settings.TOP_CONTRIBUTORS_CACHE_KEY += slugify(datetime.now())

    def tearDown(self):
        settings.TOP_CONTRIBUTORS_CACHE_KEY = self.orig_tc_cache_key


class TaggingTestCaseBase(TestCaseBase):
    """Base testcase with additional setup for testing tagging"""

    fixtures = TestCaseBase.fixtures + ['taggit.json']


def tags_eq(tagged_object, tag_names):
    """Assert that the names of the tags on tagged_object are tag_names."""
    eq_(sorted([t.name for t in tagged_object.tags.all()]),
        sorted(tag_names))
