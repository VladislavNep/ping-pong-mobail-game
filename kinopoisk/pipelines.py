# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib
from scrapy.utils.python import to_bytes
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem


class KinopoiskPipeline(object):

    def process_item(self, item, spider):
        return item


class PostersPipeline(ImagesPipeline):

    def file_path(self, request, response=None, info=None):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return 'posters/%s.jpg' % image_guid

    def get_media_requests(self, item, info):
        for poster_url in item['poster_url']:
            yield scrapy.Request(poster_url)

    def item_completed(self, results, item, info):
        poster_paths = [x['path'] for ok, x in results if ok]
        if not poster_paths:
            raise DropItem("Item contains no images")
        item['poster'] = poster_paths[0]
        return item
