# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MovieItem(scrapy.Item):
    movie_id = scrapy.Field(serializer=int)
    title = scrapy.Field()
    description = scrapy.Field()
    tagline = scrapy.Field()
    poster = scrapy.Field()
    country = scrapy.Field()
    directors = scrapy.Field()
    actors = scrapy.Field()
    world_premiere = scrapy.Field()
    rf_premiere = scrapy.Field()
    budget = scrapy.Field()
    fees_in_usa = scrapy.Field()
    fees_in_world = scrapy.Field()
    age = scrapy.Field()
    movie_shots = scrapy.Field()
    rating_kp = scrapy.Field()
    rating_imdb = scrapy.Field()
    genre = scrapy.Field()
    time = scrapy.Field()


