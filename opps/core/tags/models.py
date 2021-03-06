# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from opps.core.models import Date, Slugged


class Tag(Date, Slugged):
    name = models.CharField(_(u'Name'), max_length=255, unique=True,
                            db_index=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Tag, self).save(*args, **kwargs)

    __unicode__ = lambda self: self.name

    class Meta:
        verbose_name = _(u'Tag')
        verbose_name_plural = _(u'Tags')
        unique_together = ['slug', 'name']


class Tagged(models.Model):
    tags = models.CharField(_(u'Tags'), max_length=4000, blank=True,
                            null=True,
                            help_text=_(u'A comma-separated list of tags.'))

    def save(self, *args, **kwargs):
        if self.tags:
            #Remove empty and repeated strings on list
            tags = filter(None, set(self.tags.split(',')))
            tags = map(unicode.strip, tags)
            for tag in tags:
                Tag.objects.get_or_create(name=tag)
            self.tags = ','.join(tags)

        super(Tagged, self).save(*args, **kwargs)

    def get_tags(self):
        if self.tags:
            tags = []
            for tag in self.tags.split(','):
                if tag in ["", " "]:
                    continue
                t, created = Tag.objects.get_or_create(name=tag)
                tags.append(t)
            return tags

    class Meta:
        abstract = True
