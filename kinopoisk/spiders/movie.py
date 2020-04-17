from fake_useragent import UserAgent
import scrapy


class MovieSpider(scrapy.Spider):
    """
    Запуск паука
    scrapy crawl movie

    :returns: {
    movie_id: int,
    title: str,
    description: str,
    tagline: str,
    poster: link,
    country: str,
    directors: [],
    actors: [],
    world_premiere: str,
    budget: int,
    fees_in_usa: int,
    fees_in_world: int,
    age: int,
    movie_shots: [],
    }
    """
    name = "movie"
    HEADERS = {'user-agent': UserAgent().random, 'accept': '*/*'}
    BASE_URL = 'https://www.kinopoisk.ru'
    css = {
        'movie_items': 'div.selection-list > div.desktop-rating-selection-film-item',
        'title': 'a.selection-film-item-meta__link p.selection-film-item-meta__name::text',
        'rating_kp': 'span.film-item-user-data__rating span.rating__value::text',
        'movie_link': 'a.selection-film-item-meta__link::attr(href)',
        'movie_info': 'div.movie-info__table-container>#infoTable>table#info',
        'actors': 'div.movie-info__table-container>#actorList ul',
    }

    # def __init__(self, start_url, **kwargs):
    #     super().__init__(**kwargs)
    #     self.start_url = start_url

    def start_requests(self):
        # start_url = 'https://www.kinopoisk.ru/lists/navigator/2015-2020/?quick_filters=high_rated%2Cfilms&tab=all'
        start_url = 'https://www.kinopoisk.ru/popular/?quick_filters=films&tab=all'
        yield scrapy.Request(url=start_url, headers=self.HEADERS, callback=self.parse)

    def parse(self, response, i=1):
        print(f"Парсинг {i} страницы")
        for movie_item in response.css(self.css['movie_items']):
            movie_id = movie_item.css(self.css['movie_link']).re_first(r'([0-9]\d*)')
            title = movie_item.css(self.css['title']).get()
            rating_kp = movie_item.css(self.css['rating_kp']).get()
            yield from response.follow_all(urls=[f'{self.BASE_URL}/film/{movie_id}'],
                                           callback=self.get_movie_info, headers=self.HEADERS,
                                           cb_kwargs=dict(title=title, movie_id=movie_id, rating_kp=rating_kp))

        if self.get_next_page(response) is not None:
            i += 1
            yield response.follow(url=self.get_next_page(response), callback=self.parse, headers=self.HEADERS, cb_kwargs=dict(i=i))

    def get_movie_info(self, response, title, movie_id, rating_kp):
        world_premiere = response.css('#div_world_prem_td2 > div:nth-child(1) > a::text').get()
        rf_premiere = response.css('.rel-date_description > span:nth-child(2) > a::text').get()
        country = response.css('table.info > tr:nth-child(2) > td:nth-child(2) > div:nth-child(1) > a::text').getall()
        directors = response.xpath('//td[@itemprop="director"]/a/text()').getall()
        genre = response.xpath('//td[2]/span[@itemprop="genre"]/a/text()').getall()
        # бюджет и сборы в $
        budget = ''.join(response.css('.en > td.dollar a::text').re(r'([0-9]\d*)') or response.css('.en > td.dollar ::text').re(r'([0-9]\d*)'))
        fees_in_usa = ''.join(response.css('#div_usa_box_td2 > div:nth-child(1) > a::text').re(r'([0-9]\d*)'))
        fees_in_world_str = ''.join(response.xpath('//td[@id="div_world_box_td2"]/div[1]/a[1]/text()').re(r'([0-9=]\d*)') or response.xpath('//tr[14]/td[@class="dollar" and 2]/div[1]/a[1]').re(r'([0-9=]\d*)'))
        fees_in_world = fees_in_world_str[fees_in_world_str.rfind('=') + 1:]
        # time в мин
        time = response.css('#runtime::text').re_first(r'([0-9]\d*)')
        actors_name = response.css(self.css['actors'])[0].css('li>a::text')[:5]
        actors_id = response.css(self.css['actors'])[0].css('li>a::attr(href)')[:5]
        if actors_name.get() is not None:
            actors_name = actors_name.getall()
            actors_id = actors_id.re(r'([0-9]\d*)')
        else:
            actors_id = None
            actors_name = None

        description = response.css('.film-synopsys::text').get()
        yield {
            'title': title,
            'movie_id': movie_id,
            'rating_kp': rating_kp,
            'country': country,
            'directors': directors,
            'actors_name': actors_name,
            'genre': genre,
            'budget': budget,
            'fees_in_usa': fees_in_usa,
            'fees_in_world': fees_in_world,
            'world_premiere': world_premiere,
            'rf_premiere': rf_premiere,
            'time': time,
            'description': description,
        }

    def get_person_info(self, response):
        pass

    def get_movie_shots(self, response):
        pass

    def save_movie_poser(self):
        pass

    def save_movie_shots(self):
        pass

    def get_next_page(self, response):
        content_url = response.css('div.paginator>a.paginator__page-relative::text')[-1].get() == ('Вперёд' or 'Next')
        url = response.css('div.paginator>a.paginator__page-relative::attr(href)')[-1].get()
        return response.urljoin(url) if content_url else None

    def get_count_page(self, response):
        return response.css('div.paginator a.paginator__page-number::text')[-1].get()

#     response.selector.css('table.info > tr:nth-child(6) > td:nth-child(2) > a::text')[:3].getall()
