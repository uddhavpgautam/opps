# coding: utf-8
import json
import requests

from . import BaseShortener

class GoogleShortener(BaseShortener):
    """
    Based on:
    https://github.com/avelino/django-googl/blob/master/googl/short.py
    """
    api_url = "https://www.googleapis.com/urlshortener/v1/url"

    def short(self):
        params = json.dumps({'longUrl': self.url })
        headers = {'content-type': 'application/json'}
        response = requests.post(self.api_url, data=params,
                                 headers=headers)
        if response.ok:
            data = response.json()
            if 'id' in data:
                return data['id']
        return u''

    def expand(self):
        params = {'shortUrl': self.url }
        response = requests.get(self.api_url, params=params)
        if response.ok:
            data = response.json()
            if 'longUrl' in data:
                return data['longUrl']
        return u''


