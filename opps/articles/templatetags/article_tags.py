# -*- coding: utf-8 -*-
from django import template
from django.conf import settings
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.core.cache import cache

from opps.articles.models import ArticleBox
from opps.core.middleware import _is_mobile


register = template.Library()


@register.filter(name='is_articlebox')
def is_articlebox(slug):
    try:
        ArticleBox.objects.get(
            site=settings.SITE_ID, slug=slug,
            date_available__lte=timezone.now(),
            published=True)
        return True
    except ArticleBox.DoesNotExist:
        return False


@register.simple_tag(takes_context=True)
def get_articlebox(context, slug, template_name=None):

    is_mobile = _is_mobile(context['request'])
    cachekey = "GetArticleBox-{}-{}-{}".format(
        slug,
        template_name,
        is_mobile)

    render = cache.get(cachekey)
    if render:
        return render

    try:
        box = ArticleBox.objects.get(site=settings.SITE_ID, slug=slug,
                                     date_available__lte=timezone.now(),
                                     published=True)
    except ArticleBox.DoesNotExist:
        box = None

    t = template.loader.get_template('articles/articlebox_detail.html')
    if template_name:
        t = template.loader.get_template(template_name)

    render = t.render(template.Context({
        'articlebox': box,
        'slug': slug,
        'context': context
    }))

    cache.set(cachekey, render, 3600)

    return render


@register.simple_tag(takes_context=True)
def get_articlebox_group(context, position, **kwargs):

    template_name = kwargs.get('template_name', None)
    slug = kwargs.get('partial_slug', None)

    articleboxes = ArticleBox.objects.filter(
        site=settings.SITE_ID, slug__icontains=slug,
        date_available__lte=timezone.now(),
        order=position, published=True
    )

    t = template.loader.get_template('articles/articlebox_group.html')
    if template_name:
        t = template.loader.get_template(template_name)

    return t.render(template.Context({
        'articleboxes': articleboxes,
        'slug': slug,
        'context': context
    }))


@register.simple_tag
def get_all_articlebox(channel_long_slug, template_name=None):
    boxes = ArticleBox.objects.filter(
        site=settings.SITE_ID,
        date_available__lte=timezone.now(),
        published=True,
        channel_long_slug=channel_long_slug)

    t = template.loader.get_template('articles/articlebox_list.html')
    if template_name:
        t = template.loader.get_template(template_name)

    return t.render(template.Context({'articleboxes': boxes}))


@register.simple_tag
def get_post_content(post, template_name='articles/post_related.html',
                     content_field='content', related_name='related_posts',
                     get_related=True, safe=True, divider="<br />",
                     placeholder=settings.OPPS_RELATED_POSTS_PLACEHOLDER):
    """
    takes the post and tries to find the related posts to embed inside
    the content, if not found return only the content.

    post:
        Post instance
    template_name:
        path to template which receives the related posts
    content_field:
        name of the field with post content
    related_name:
        a m2m field name or a @property name which
        returns a queryset of related posts
    get_related:
        if False bypass and return only the content
    safe:
        if True mark the content as safe
    divider:
        used when there is no placeholder
    placeholder:
        the string to replace ex: --related--
    """
    if not hasattr(post, content_field):
        return None
    content = getattr(post, content_field, '')
    if not get_related:
        return content

    related_posts = getattr(post, related_name, None)

    if not related_posts.exists():
        return mark_safe(content)

    # GET THE TEMPLATE
    t = template.loader.get_template(template_name)
    related_rendered = t.render(
        template.Context({'post': post, related_name: related_posts})
    )
    # EMBED RELATED POSTS
    if placeholder in content:
        return mark_safe(content.replace(
            placeholder,
            related_rendered
        ))
    else:
        return mark_safe(content + divider + related_rendered)


@register.inclusion_tag('articles/album_related.html')
def get_album_related_articles(context):
    return {'album': context}
