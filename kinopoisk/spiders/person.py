import json
import random
from scrapy.loader.processors import Join
import scrapy
from fake_useragent import UserAgent
from kinopoisk.items import PersonItem, PersonLoader


class PersonSpider(scrapy.Spider):

    name = "person"
    custom_settings = {
        'ITEM_PIPELINES': {
            'scrapy.pipelines.images.ImagesPipeline': 1,
            'kinopoisk.pipelines.PersonPhotoPipeline': 300,
        }
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_path = '/home/vladislav/PycharmProjects/kinopoisk-api/person.json'
        self.HEADERS = {
            'User-Agent': UserAgent().random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        self.BASE_URL = 'https://www.kinopoisk.ru'
        self.css = {
            'item_type': '.info > tr',
            'name': 'h1.moviename-big::text',
            'photo': '.film-img-box img[itemprop="image"]::attr(src)',
            'description': 'ul.trivia > li.trivia::text',
        }
        self.proxy_pool = ['113.120.37.253:10098']

    def get_person_id(self, file_path):
        res = set()
        with open(file_path, 'r') as f:
            data = json.loads(f.read())
            for i in data:
                res.update(i["roles"])
        return res

    def start_requests(self):
        for person_id in self.get_person_id(self.file_path):
            url = f'https://www.kinopoisk.ru/name/{person_id}/view_info/ok/#trivia'
            yield scrapy.Request(
                url=url,
                headers=self.HEADERS,
                callback=self.parse_info,
                # meta=dict(proxy=random.choice(self.proxy_pool)),
                cb_kwargs=dict(person_id=person_id)
            )

    def parse_info(self, response, person_id):
        print(f"Парсим пользователя {person_id}")
        loader = PersonLoader(item=PersonItem(), response=response)
        loader.add_css('name', self.css['name'])
        loader.add_css('photo_url', self.css['photo'])
        loader.add_css('description', self.css['description'], Join(separator=' '))

        for info in response.css(self.css['item_type']):
            if info.css('td.type::text').get() == 'карьера':
                roles = info.css('td')[1].css('a::text').getall()
                loader.add_value('roles', roles)

            elif info.css('td.type::text').get() == 'дата рождения':
                birthday = info.css('td.birth>a::text').getall()
                loader.add_value('birthday', birthday)

            elif info.css('td.type::text').get() == 'жанры':
                genre = info.css('td')[1].css('a::text').getall()
                loader.add_value('genre', genre)

            elif info.css('td.type::text').get() == 'всего фильмов':
                total_movies = info.css('td')[1].css('::text').re_first(r'([0-9]\d*)')
                loader.add_value('total_movies', total_movies)

        yield loader.load_item()
