# -*- coding: utf-8 -*-
import scrapy
import hashlib
from PIL import Image
from pathlib import Path
from scrapy.utils.python import to_bytes
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from kinopoisk.items import MovieItem, MovieIdItem, PersonIdItem, PersonItem


class KinopoiskPipeline(object):

    def process_item(self, item, spider):
        return item


class PostersPipeline(ImagesPipeline):

    def file_path(self, request, response=None, info=None):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return 'posters/%s.jpg' % image_guid

    def item_completed(self, results, item, info):
        poster_paths = [x['path'] for ok, x in results if ok]
        if not poster_paths:
            raise DropItem("Item contains no images")
        item['poster'] = poster_paths[0]
        return item


class MovieShotsPipeline(ImagesPipeline):

    def file_path(self, request, response=None, info=None):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return 'movie_shots/%s.jpg' % image_guid

    def item_completed(self, results, item, info):
        for ok, x in results:
            if ok:
                img = Image.open(Path('kinopoisk/img/' + x['path']))
                width = img.size[0]
                height = img.size[1]
                crop_img = img.crop((0, 0, width, height - 50))
                crop_img.save(Path('kinopoisk/img/' + x['path']))

        movie_shots_paths = [x['path'] for ok, x in results if ok]
        if not movie_shots_paths:
            raise DropItem("Item contains no images")
        item['movie_shots'] = movie_shots_paths
        return item


class PersonPhotoPipeline(ImagesPipeline):

    def file_path(self, request, response=None, info=None):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return 'person/%s.jpg' % image_guid

    def get_media_requests(self, item, info):
        for image_url in item['photo_url']:
            yield scrapy.Request(image_url)

    def item_completed(self, results, item, info):
        poster_paths = [x['path'] for ok, x in results if ok]
        if not poster_paths:
            raise DropItem("Item contains no images")
        item['photo'] = poster_paths[0]
        return item
