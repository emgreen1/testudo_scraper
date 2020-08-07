#file to define items coresponding to their respective django models in
#testudo app 
#uses scrapy_djangoitem and defines the fields of the item based on the model
import scrapy
import scrapy_djangoitem

from scrapy_djangoitem import DjangoItem
from testudo.models import Departments, Classes

class DepartmentItem(DjangoItem):
    django_model = Departments

class ClassItem(scrapy.Item):
    cid = scrapy.Field()
    title = scrapy.Field()
    mincredits = scrapy.Field()
    maxcredits = scrapy.Field()
    geneds = scrapy.Field()
    descrip = scrapy.Field()
    dept_abrev_term = scrapy.Field()

class SectionItem(scrapy.Item):
    cid = scrapy.Field()
    sectionid = scrapy.Field()
    professor = scrapy.Field()
    totalseats = scrapy.Field()
    openseats = scrapy.Field()
    waitlist = scrapy.Field()
    holdfile = scrapy.Field()
    days = scrapy.Field()
    starttime = scrapy.Field()
    endtime = scrapy.Field()
    building = scrapy.Field()
    classroom = scrapy.Field()
    online = scrapy.Field()


