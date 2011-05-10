import json

from django.conf import settings
from django.core.cache import cache

from nose.tools import eq_
from pyquery import PyQuery as pq

from customercare.tests import cc_category, cc_response
from sumo.urlresolvers import reverse
from sumo.tests import TestCase


class CannedResponsesTestCase(TestCase):
    """Canned responses tests."""

    def test_empty_canned_responses(self):
        """When no canned responses are available, fall back to a message."""
        r = self.client.get(reverse('customercare.landing'), follow=True)
        eq_(200, r.status_code)
        doc = pq(r.content)
        assert doc('#no-responses'), 'Fallback message is not showing up.'
        assert doc('#no-responses .email'), 'Must haz contact email.'

    def test_list_canned_responses(self):
        """Listing canned responses works as expected."""
        c1 = cc_category(weight=0, save=True)
        c2 = cc_category(weight=20, save=True)
        c3 = cc_category(locale='fr', save=True)
        r1 = cc_response(categories=[(c1, 0)])
        r2 = cc_response(categories=[(c1, 1), (c2, 0)])
        r3 = cc_response(categories=[(c1, 2), (c2, 1), (c3, 0)])
        r4 = cc_response(categories=[(c3, 1)])

        r = self.client.get(reverse('customercare.landing'), follow=True)
        eq_(200, r.status_code)
        doc = pq(r.content)
        responses_plain = doc('#accordion').text()
        assert r1.title in responses_plain
        assert r4.title not in responses_plain
        assert r3.title in responses_plain
        # Ordering works for categories.
        assert responses_plain.find(c1.title) < responses_plain.find(c2.title)
        # And for responses within a category.
        assert responses_plain.find(r1.title) < responses_plain.find(r2.title)
        assert responses_plain.find(r2.title) < responses_plain.find(r3.title)

        # Listing 5 responses: r1 x 3, r2 x 2, r3 x 1
        eq_(5, len(doc('#accordion a.reply-topic')))


class TweetListTestCase(TestCase):
    """Tests for the list of tweets."""

    def test_fallback_message(self):
        """Fallback message when there are no tweets."""
        r = self.client.get(reverse('customercare.landing'), follow=True)
        eq_(200, r.status_code)
        doc = pq(r.content)
        assert doc('#tweets-wrap .warning-box'), (
               'Fallback message is not showing up.')


class StatsTests(TestCase):
    """Tests for the activity and contributors stats."""

    def setUp(self):
        super(StatsTests, self).setUp()
        with open('apps/customercare/tests/stats.json') as f:
            self.json_data = json.load(f)

    def tearDown(self):
        cache.delete(settings.CC_TWEET_ACTIVITY_CACHE_KEY)
        cache.delete(settings.CC_TOP_CONTRIB_CACHE_KEY)
        super(StatsTests, self).tearDown()

    def test_activity_contributors(self):
        """Activity and contributors stats are both set."""
        cache.set(settings.CC_TWEET_ACTIVITY_CACHE_KEY,
                  self.json_data['activity'],
                  settings.CC_STATS_CACHE_TIMEOUT)
        cache.set(settings.CC_TOP_CONTRIB_CACHE_KEY,
                  self.json_data['contributors'],
                  settings.CC_STATS_CACHE_TIMEOUT)
        r = self.client.get(reverse('customercare.landing'), follow=True)
        eq_(200, r.status_code)

    def test_activity_only(self):
        """Only activity stats are set."""
        cache.set(settings.CC_TWEET_ACTIVITY_CACHE_KEY,
                  self.json_data['activity'],
                  settings.CC_STATS_CACHE_TIMEOUT)
        r = self.client.get(reverse('customercare.landing'), follow=True)
        eq_(200, r.status_code)

    def test_contributors_only(self):
        """Only contributors stats are set."""
        cache.set(settings.CC_TOP_CONTRIB_CACHE_KEY,
                  self.json_data['contributors'],
                  settings.CC_STATS_CACHE_TIMEOUT)
        r = self.client.get(reverse('customercare.landing'), follow=True)
        eq_(200, r.status_code)
