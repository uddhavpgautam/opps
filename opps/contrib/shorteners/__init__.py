#coding: utf-8
from django.core.validators import URLValidator, ValidationError


class BaseShortener(object):
    def __init__(self, url):
        self.url = url

        if isinstance(url, unicode):
            self.url = url.encode('utf-8')

        url_validator = URLValidator()
        try:
            url_validator(self.url)
        except ValidationError:
            return u""

    def short(self):
        """
        Method used to short url
        """
        raise NotImplementedError()

    def expand(self):
        """
        Method used to unshort url
        """
        raise NotImplementedError()
