#apps.py file to allow for django to recognize this as an application

from django.apps import AppConfig

class Testudo_scraperConfig(AppConfig):
    name = 'testudo_scraper'

