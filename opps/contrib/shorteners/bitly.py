# coding: utf-8
import requests

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

from . import BaseShortener

class BitlyShortener(BaseShortener):
    shorten_url = 'http://api.bit.ly/shorten'
    expand_url = 'http://api.bit.ly/expand'

    def __init__(self, *args, **kwargs):
        if not settings.BITLY_LOGIN and not settings.BITLY_API_KEY:
            raise ImproperlyConfigured(_(u'Bit.ly credentials not found in '
                                       u'settings.'))

        super(BitlyShortener, self).__init__(*args, **kwargs)

    def short(self):
        params = dict(
            version="2.0.1",
            longUrl=self.url,
            login=settings.BITLY_LOGIN,
            apiKey=settings.BITLY_API_KEY,
        )
        response = requests.post(self.shorten_url, data=params)
        if response.ok:
            data = response.json()
            if 'statusCode' in data and data['statusCode'] == 'OK':
                key = self.url
                return data['results'][key]['shortUrl']
        return u''

    def expand(self):
        params = dict(
            version="2.0.1",
            shortUrl=self.url,
            login=settings.BITLY_LOGIN,
            apiKey=settings.BITLY_API_KEY,
        )
        response = requests.get(self.expand_url, params=params)
        if response.ok:
            data = response.json()
            if 'statusCode' in data and data['statusCode'] == 'OK':
                # get the hash key that contains the longUrl
                hash_key = data['results'].keys()[0]
                return data['results'][hash_key]['longUrl']
        return u''


