from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from fact_check_crawler.spiders.boatosorg import BoatosSpider
 
 
process = CrawlerProcess(get_project_settings())
process.crawl(BoatosSpider)
process.start()