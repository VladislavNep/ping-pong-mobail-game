import json
from fake_useragent import UserAgent
from scrapy.loader.processors import Join
import scrapy
from kinopoisk.tormanager import ConnectionManager
from kinopoisk.items import PersonItem, PersonLoader


class PersonSpider(scrapy.Spider):
    name = "person"
    custom_settings = {
        'ITEM_PIPELINES': {
            'scrapy.pipelines.images.ImagesPipeline': 1,
            'kinopoisk.pipelines.PersonPhotoPipeline': 300,
        },

        "DOWNLOAD_DELAY": 5,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
        "CONCURRENT_REQUESTS": 2,

        'FEEDS': {
            'tmp/person.json': {
                'format': 'json',
                'encoding': 'utf8',
                'store_empty': False,
                'fields': None,
                'indent': 0,
            }
        },

    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_path = 'tmp/person_id.json'
        self.BASE_URL = 'https://www.kinopoisk.ru'
        self.css = {
            'item_type': '.info > tr',
            'name': 'h1.moviename-big::text',
            'photo': '.film-img-box img[itemprop="image"]::attr(src)',
            'photo2': '.film-img-box a img[itemprop="image"]::attr(src)',
            'description': 'ul.trivia > li.trivia::text',
        }
        self.cm = ConnectionManager('password')

    def get_person_id(self, file_path):
        res = set()
        with open(file_path, 'r') as f:
            data = json.loads(f.read())
            for i in data:
                res.update(i["person_id"])
        return res

    def start_requests(self):
        _count_req = 0

        for person_id in self.get_person_id(self.file_path):
            _count_req += 1
            if _count_req >= 30:
                self.cm.new_identity()
                _count_req = 0

            url = f'https://www.kinopoisk.ru/name/{person_id}/view_info/ok/'
            yield scrapy.Request(
                url=url,
                callback=self.parse_info,
                cb_kwargs=dict(person_id=person_id),
                meta=dict(proxy='127.0.0.1:8118'),
                headers={
                    'User-Agent': UserAgent().random,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Referer': 'https://yandex.ru/',
                    'Host': 'www.kinopoisk.ru'
                },

            )

    def parse_info(self, response, person_id):
        print(f"Парсим пользователя {person_id}")
        print('meta: ', response.meta)
        loader = PersonLoader(item=PersonItem(), response=response)
        loader.add_css('name', self.css['name'])
        loader.add_css('description', self.css['description'], Join(separator=' '))

        photo_url = response.css(self.css['photo']).get()
        if not photo_url:
            photo_url = response.css(self.css['photo2']).get()
        if photo_url:
            loader.add_value('photo_url', photo_url)

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
