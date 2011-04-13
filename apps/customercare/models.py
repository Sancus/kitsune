from datetime import datetime
import json

from django.db import models

from sumo.models import ModelBase, LocaleField


class Tweet(ModelBase):
    """An entry on twitter."""
    tweet_id = models.BigIntegerField(primary_key=True)
    raw_json = models.TextField()
    # This is different from our usual locale, so not using LocaleField.
    locale = models.CharField(max_length=20, db_index=True)
    created = models.DateTimeField(default=datetime.now, db_index=True)
    reply_to = models.ForeignKey('self', null=True, related_name='replies')
    hidden = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ('-tweet_id',)

    @classmethod
    def latest(cls):
        """Return the most recent tweet.

        Raise Tweet.DoesNotExist if there are None.

        This is like Tweet.objects.latest(), except it sorts by tweet_id rather
        than a date column.

        """
        return cls.objects.order_by('-tweet_id')[0:1].get()

    def __unicode__(self):
        tweet = json.loads(self.raw_json)
        return tweet['text']


class CannedCategory(ModelBase):
    """Category for canned responses."""
    title = models.CharField(max_length=255)
    weight = models.IntegerField(
        default=0, db_index=True,
        help_text='Heavier items sink, lighter ones bubble up.')
    locale = LocaleField(db_index=True)

    class Meta:
        ordering = ('locale', 'weight', 'title')
        unique_together = ('title', 'locale')
        verbose_name_plural = 'Canned categories'

    def __unicode__(self):
        return u'[%s] %s' % (self.locale, self.title)


class CannedResponse(ModelBase):
    """Canned response to tweets."""
    title = models.CharField(max_length=255)
    response = models.CharField(max_length=140)
    categories = models.ManyToManyField(
        CannedCategory, related_name='responses', through='CategoryMembership')
    locale = LocaleField(db_index=True)

    class Meta:
        ordering = ('locale', 'title')
        unique_together = ('title', 'locale')

    def __unicode__(self):
        return u'[%s] %s' % (self.locale, self.title)


class CategoryMembership(ModelBase):
    """Mapping table for canned responses <-> categories."""
    category = models.ForeignKey(CannedCategory, blank=True)
    response = models.ForeignKey(CannedResponse, blank=True)
    weight = models.IntegerField(
        default=0, db_index=True,
        help_text='Heavier items sink, lighter ones bubble up.')

    def __unicode__(self):
        return '%s in %s' % (self.response.title, self.category.title)
