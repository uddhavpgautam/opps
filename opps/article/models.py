# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from tagging.fields import TagField
from googl.short import GooglUrlShort

from opps.core.models import Publishable


class Article(Publishable):
    title = models.CharField(_(u"Title"), max_length=140)
    slug = models.SlugField(_(u"URL"), max_length=150, unique=True,
                            db_index=True)
    short_url = models.URLField(_("Short URL"), blank=False, null=True)
    short_title = models.CharField(_(u"Short title"), max_length=140,
                                   blank=False, null=True)
    headline = models.TextField(_(u"Headline"), blank=True)
    channel = models.ForeignKey('channel.Channel', verbose_name=_(u"Channel"))

    main_image = models.ForeignKey('image.Image',
                                   verbose_name=_(u'Main Image'), blank=False,
                                   null=True, on_delete=models.SET_NULL)

    images = models.ManyToManyField('image.Image', null=True, blank=True,
                                    related_name='article_images',
                                    through='article.ArticleImage')
    sources = models.ManyToManyField('source.Source', null=True, blank=True,
                                     through='article.ArticleSource')

    tags = TagField(null=True, verbose_name=_(u"Tags"))

    def __absolute_url(self):
        return "{0}/{1}".format(self.channel, self.slug)

    def get_absolute_url(self):
        return "http://{0}".format(self.__absolute_url())
    get_absolute_url.short_description = 'URL'

    def __unicode__(self):
        return self.__absolute_url()

    def save(self, *args, **kwargs):
        if not self.short_url:
            self.short_url = GooglUrlShort(self.get_absolute_url()).short()
        super(Article, self).save(*args, **kwargs)


class Post(Article):
    content = models.TextField(_(u"Content"))
    album = models.ManyToManyField('Album', related_name='post_album',
                                   null=True, blank=True)


class Album(Article):
    pass


class ArticleSource(models.Model):
    article = models.ForeignKey('article.Article', verbose_name=_(u'Article'), null=True,
                             blank=True, related_name='articlesource_article',
                             on_delete=models.SET_NULL)
    source = models.ForeignKey('source.Source', verbose_name=_(u'Source'), null=True,
                               blank=True, related_name='articlesource_source',
                               on_delete=models.SET_NULL)
    order = models.PositiveIntegerField(_(u'Order'), default=0)

    def __unicode__(self):
        return self.source.slug


class ArticleImage(models.Model):
    article = models.ForeignKey('article.Article', verbose_name=_(u'Article'), null=True,
                             blank=True, related_name='articleimage_article',
                             on_delete=models.SET_NULL)
    image = models.ForeignKey('image.Image', verbose_name=_(u'Image'), null=True,
                              blank=True, on_delete=models.SET_NULL)
    order = models.PositiveIntegerField(_(u'Order'), default=0)

    def __unicode__(self):
        return self.image.title


class ArticleBox(Publishable):
    name = models.CharField(_(u"Box name"), max_length=140)
    slug = models.SlugField(_(u"Slug"), max_length=150,
                            unique=True, db_index=True)
    post = models.ForeignKey(Post, null=True, blank=True,
                             on_delete=models.SET_NULL)
    channel = models.ForeignKey('channel.Channel', null=True, blank=True,
                             on_delete=models.SET_NULL)
    posts = models.ManyToManyField(Post, null=True, blank=True,
                                   related_name='articlebox_post',
                                   through='article.ArticleBoxPost')

    def __unicode__(self):
        return self.slug


class ArticleBoxPost(models.Model):
    post = models.ForeignKey(Post, verbose_name=_(u'Article Box Post'), null=True,
                             blank=True, related_name='articleboxpost_post',
                             on_delete=models.SET_NULL)
    articlebox = models.ForeignKey(ArticleBox, verbose_name=_(u'Article Box'), null=True,
                                   blank=True, related_name='articlebox',
                                   on_delete=models.SET_NULL)

    def __unicode__(self):
        return "{0}-{1}".format(self.articlebox.slug, self.post.slug)
