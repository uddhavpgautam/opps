#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from opps.core.models import Publishable, Channeling


class QuerySet(Publishable):
    name = models.CharField(_(u"Dynamic queryset name"), max_length=140)
    slug = models.SlugField(
        _(u"Slug"),
        db_index=True,
        max_length=150,
        unique=True,
    )

    model = models.CharField(_(u'Model'), max_length=150)
    limit = models.PositiveIntegerField(_(u'Limit'), default=7)
    offset = models.PositiveIntegerField(_(u'Offset'), default=0)
    order_field = models.CharField(
        _(u"Order Field"),
        max_length=100,
        default='id',
        help_text=_(u"Take care, should be an existing field or lookup")
    )
    order = models.CharField(_('Order'), max_length=1, choices=(
        ('-', 'DESC'), ('+', 'ASC')))
    channel = models.ForeignKey(
        'channels.Channel',
        verbose_name=_(u"Channel"),
        blank=True,
        null=True
    )

    filters = models.TextField(
        _(u'Filters'),
        help_text=_(u'Json format extra filters for queryset'),
        blank=True,
        null=True
    )

    def __init__(self, *args, **kwargs):
        """
        to avoid re-execution of methods
        its results are cached in a local storage
        per instance cache
        """
        super(QuerySet, self).__init__(*args, **kwargs)
        if not hasattr(self, 'local_cache'):
            self.local_cache = {}

    def __unicode__(self):
        return u"{} {} {}".format(self.name, self.slug, self.model)

    def clean(self):

        if self.filters:
            try:
                json.loads(self.filters)
            except:
                raise ValidationError(_(u'Invalid JSON'))

        try:
            self.get_queryset().all()
        except Exception as e:
            raise ValidationError(
                u'Invalid Queryset: {}'.format(str(e))
            )

        if self.offset >= self.limit:
            raise ValidationError(_(u'Offset can\'t be equal or higher than'
                                    u'limit'))

    def get_queryset(self, content_group='default',
                     exclude_ids=None, use_local_cache=True):
        cached = self.local_cache.get('get_queryset')
        if use_local_cache and cached:
            return cached

        exclude_ids = exclude_ids or []

        _app, _model = self.model.split('.')
        model = models.get_model(_app, _model)

        queryset = model.objects.filter(
            published=True,
            date_available__lte=timezone.now(),
            site=self.site
        ).exclude(child_class='Mirror')

        try:
            if model._meta.get_field_by_name('show_on_root_channel'):
                queryset = queryset.filter(show_on_root_channel=True)
        except:
            pass  # silently pass when FieldDoesNotExists

        if self.channel and not self.channel.homepage:
            queryset = queryset.filter(channel=self.channel)

        if self.filters:
            filters = json.loads(self.filters)
            queryset = queryset.filter(**filters)

        # importing here to avoid circular imports
        from opps.containers.models import Container
        if issubclass(model, Container):
            queryset = queryset.exclude(
                id__in=exclude_ids
            )

        if self.order == '-':
            order_term = "-{}".format(self.order_field or 'id')
        else:
            order_term = self.order_field or 'id'

        queryset = queryset.order_by(order_term)

        result = queryset[self.offset:self.limit]
        if use_local_cache:
            self.local_cache['get_queryset'] = result
        return result


class BaseBox(Publishable, Channeling):
    name = models.CharField(_(u"Box name"), max_length=140)

    slug = models.SlugField(
        _(u"Slug"),
        db_index=True,
        max_length=150,
    )

    class Meta:
        abstract = True
        unique_together = ['site', 'channel_long_slug', 'slug']

    def __unicode__(self):
        return u"{}-{}".format(self.slug, self.site.name)
