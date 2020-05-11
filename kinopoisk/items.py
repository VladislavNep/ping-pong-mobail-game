# -*- coding: utf-8 -*-

from scrapy.utils.python import to_unicode
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join, Identity, Compose


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


def str_list_to_int(value):
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
    trailer = scrapy.Field()
    movie_shots = scrapy.Field()
    movie_shot_urls = scrapy.Field()
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
    trailer_out = TakeFirst()

    time_in = MapCompose(str_to_int)
    time_out = TakeFirst()

    rating_kp_in = MapCompose(str_to_float)
    rating_kp_out = TakeFirst()

    rating_imdb_in = MapCompose(str_to_float)
    rating_imdb_out = TakeFirst()

    budget_in = MapCompose(str_to_int)
    budget_out = TakeFirst()

    country_out = TakeFirst() if MapCompose(lambda value: len(value) == 1) else Identity()
    directors_out = TakeFirst() if MapCompose(lambda value: len(value) == 1) else Identity()

    fees_in_usa_in = MapCompose(str_to_int)
    fees_in_usa_out = TakeFirst()

    fees_in_world_in = MapCompose(str_to_int)
    fees_in_world_out = TakeFirst()


class MovieIdItem(scrapy.Item):
    movie_id = scrapy.Field()


class MovieIdLoader(ItemLoader):
    default_output_processor = MapCompose()


class PersonIdItem(scrapy.Item):
    person_id = scrapy.Field()


class PersonIdLoader(ItemLoader):
    person_id_out = Compose(str_list_to_int)


class PersonItem(scrapy.Item):
    name = scrapy.Field()
    roles = scrapy.Field()
    birthday = scrapy.Field()
    genre = scrapy.Field()
    total_movies = scrapy.Field()
    photo = scrapy.Field()
    photo_url = scrapy.Field()
    description = scrapy.Field()
    place_of_birth = scrapy.Field()


class PersonLoader(ItemLoader):
    name_in = MapCompose(lambda v: v.split())
    name_out = Join()

    birthday_in = Join()
    birthday_out = TakeFirst()

    roles_in = Compose(lambda value: [i.strip() for i in value])

    total_movies_in = MapCompose(str_to_int)
    total_movies_out = TakeFirst()

    description_in = MapCompose(replace_chars)
    description_out = TakeFirst()
