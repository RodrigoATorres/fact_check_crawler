import os
import scrapy
from fact_check_crawler.items import Article
from fact_check_crawler.mongo_provider import MongoProvider
import socket
import urllib.request

class BoatosSpider(scrapy.Spider):
    name = "boatos.org"
    allowed_domains = ['boatos.org']
    start_urls = ['https://www.boatos.org/']

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        kwargs['mongo_uri'] = crawler.settings.get("MONGO_URI")
        kwargs['mongo_database'] = crawler.settings.get('MONGO_DATABASE')
        return super(BoatosSpider, cls).from_crawler(crawler, *args, **kwargs)

    def __init__(self, mongo_uri=None, mongo_database=None, *args, **kwargs):
        super(BoatosSpider, self).__init__(*args, **kwargs)
        self.mongo_provider = MongoProvider(mongo_uri, mongo_database)
        self.collection = self.mongo_provider.get_collection()

    def parse(self, response):
        links = response.css("li.cat-item > a::attr(href)").getall()
        for link in links:
            print(response.urljoin(link))
            yield scrapy.Request(
                response.urljoin(link),
                callback = self.parse_category
            )

    def parse_category(self, response):
        links = response.css(".more-link::attr(href)").getall()
        for link in links:
            if self.collection.find_one({'url':link}):
                print('url already registered')
                continue
            yield scrapy.Request(
                response.urljoin(link),
                callback = self.parse_article
        )

        pages_url = response.css('.previous > a:nth-child(1)::attr(href)').getall()
        pages_url += response.css('.next > a:nth-child(1)::attr(href)').getall()

        for page in pages_url:
            yield scrapy.Request(
                response.urljoin(page),
                callback=self.parse_category
            )

    def parse_article(self, response):
        try:
            urllib.request.urlopen(os.environ.get('HEALTH_CHECK_URL_ARTICLE'), timeout=10)
        except socket.error as e:
            # Log ping failure here...
            print("Ping failed: %s" % e)

        hoaxes = response.css('span[style="color: #ff0000;"] *::text').getall()
        hoaxes = list(filter(lambda x:x!='Se inscreva no nosso canal no Youtube', hoaxes))
        if len(hoaxes) == 0:
            hoaxes = response.css('.entry-content > p > em *::text').getall()

        title = response.css('.entry-title::text').get().strip()
        datetime = response.css('.entry-date::attr(datetime)').get()

        if response.css('.entry-content > p:nth-child(2) > strong:nth-child(1)::text').get() != None:
            summary = response.css('.entry-content > p:nth-child(2) > strong:nth-child(1)::text').get().strip()
        else:
            summary = title


        yield Article(
            title = title,
            datetime = datetime,
            summary = summary,
            hoax = ''.join(hoaxes),
            url = response.url
        )
