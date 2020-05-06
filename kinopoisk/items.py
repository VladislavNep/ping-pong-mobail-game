# -*- coding: utf-8 -*-

from scrapy.utils.python import to_unicode
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join, Identity
import regex as re


def replace_chars(text, which_ones=('\n', '\t', '\x85', '\x97'), replace_by=u'', encoding=None):
    """Remove escape characters.

    `which_ones` is a tuple of which escape characters we want to remove.
    By default removes ``\\n``, ``\\t``, ``\\x85``, ``\\x97``.

    `replace_by` is the string to replace the escape characters by.
    It defaults to ``''``, meaning the escape characters are removed.

    """

    text = to_unicode(text, encoding)
    for ec in which_ones:
        text = text.replace(ec, to_unicode(replace_by, encoding))
    return text


def str_to_int(value):
    return int(value) if value.isdigit() else value


def str_to_float(value):
    return float(value)


def str_lst_to_int(value):
    result = [int(x) for x in value if x.isdigit()]
    return result


class MovieItem(scrapy.Item):
    title = scrapy.Field()
    description = scrapy.Field()
    poster = scrapy.Field()
    poster_url = scrapy.Field()
    country = scrapy.Field()
    directors = scrapy.Field()
    actors = scrapy.Field()
    world_premier = scrapy.Field()
    rf_premiere = scrapy.Field()
    budget = scrapy.Field()
    fees_in_usa = scrapy.Field()
    fees_in_world = scrapy.Field()
    age = scrapy.Field()
    movie_shots = scrapy.Field()
    movie_shot_urls = scrapy.Field()
    img_promo = scrapy.Field()
    img_promo_urls = scrapy.Field()
    rating_kp = scrapy.Field()
    rating_imdb = scrapy.Field()
    genre = scrapy.Field()
    time = scrapy.Field()


class MovieLoader(ItemLoader):

    default_input_processor = MapCompose(replace_chars)
    description_out = TakeFirst()
    title_out = TakeFirst()
    world_premier_out = TakeFirst()
    rf_premiere_out = TakeFirst()

    time_in = MapCompose(str_to_int)
    time_out = TakeFirst()

    rating_kp_in = MapCompose(lambda value: float(value))
    rating_kp_out = TakeFirst()

    budget_in = MapCompose(str_to_int)
    budget_out = TakeFirst()

    country_out = TakeFirst() if (lambda value: len(value) == 1) else Identity()
    directors_out = TakeFirst() if (lambda value: len(value) == 1) else Identity()

    fees_in_usa_in = MapCompose(str_to_int)
    fees_in_usa_out = TakeFirst()

    fees_in_world_in = MapCompose(str_to_int)
    fees_in_world_out = TakeFirst()


class MovieIdItem(scrapy.Item):
    movie_id = scrapy.Field(serializer=int)


class MovieIdLoader(ItemLoader):
    default_output_processor = MapCompose()


class PersonIdItem(scrapy.Item):
    person_id = scrapy.Field(serializer=int)


class PersonIdLoader(ItemLoader):
    person_id_in = MapCompose(str_lst_to_int)
