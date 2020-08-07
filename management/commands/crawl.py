#run with python manage.py crawl on command line
#runs the testudo scraper using the models defined in the testudo app
#must specify settings in order to work 

from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from ...testudo_scraper import settings as my_settings
from ...testudo_scraper.spiders import TestudoSpider

class Command(BaseCommand):
    help = "Release the spiders for Testudo"

    def handle(self, *args, **options):
        crawler_settings = Settings()
        crawler_settings.setmodule(my_settings)

        process = CrawlerProcess(settings=crawler_settings)

        process.crawl(TestudoSpider.TestudoSpider)
        process.start()

