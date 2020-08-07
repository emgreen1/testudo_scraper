# -*- coding: utf-8 -*-
import scrapy

from testudo_scraper.testudo_scraper.items import DepartmentItem, ClassItem, SectionItem

TERM = '202008'

class TestudoSpider(scrapy.Spider):
    name = 'TestudoSpider'
    allowed_domains = ['app.testudo.umd.edu']
    start_urls = ['http://app.testudo.umd.edu/soc/' + TERM + '/']

    def parse(self, response):
        departments = response.xpath('//div[@class="course-prefix row"]/a')
        links = departments.xpath('./@href').extract()

        for department, link  in zip(departments, links):
            item = DepartmentItem()
            item['dept_abrev'] = department.xpath('./span[@class="prefix-abbrev push_one two columns"]/text()').get()
            item['dept_name'] = department.xpath('./span[@class="prefix-name nine columns"]/text()').get()
            item['dept_abrev_term'] = TERM + str(item['dept_abrev'])

            yield item

            if link is not None:
                link = link.split("/")[1]
                yield response.follow(link, callback=self.parse_class, cb_kwargs=dict(term=item['dept_abrev_term']))


    def parse_class(self, response, term):
        course_id = response.xpath('//div[@class="courses-container"]/div[@class="course"]/input/@value').getall()
        
        for cid in course_id:
            item = ClassItem()
            item['dept_abrev_term'] = term
                
            class_path = '//div[@class="courses-container"]/div[@id="' + cid + '"]'
            _class_ = response.xpath(class_path)

            item['cid'] = str(cid)
            item['title'] = _class_.xpath('.//span[@class="course-title"]/text()').get()
            item['mincredits'] = _class_.xpath('.//span[@class="course-min-credits"]/text()').get()
            item['maxcredits'] = _class_.xpath('.//span[@class="course-max-credits"]/text()').get()

            if not _class_.xpath('.//span[@class="course-subcategory"]/a/text()').getall():
                item['geneds'] = None
            else:
                strings_check = _class_.xpath('.//div[@class="gen-ed-codes-group six columns"]/div/text()').getall()
                check = False
                for string in strings_check:
                    if 'or' in string:
                        check = True
                    if check:
                        geneds = _class_.xpath('.//span[@class="course-subcategory"]/a/text()').getall()
                        geneds[0] += 'c'
                        geneds[1] += 'c'

                        item['geneds'] = geneds
                    else:
                        item['geneds'] = _class_.xpath('.//span[@class="course-subcategory"]/a/text()').getall()

            item['descrip'] = _class_.xpath('.//div[@class="approved-course-text"]/text()').get()
                    
            yield item

        for cid in course_id:
            url = response.url + '/' + cid
            request = scrapy.Request(url, callback=self.parse_section, cb_kwargs=dict(cid=cid))
            yield request

    def parse_section(self, response, cid):
        section_type = {}
        section_type['f2f'] = response.xpath('//div[@id="' + cid + '"]//div[@class="toggle-sections-link-container"]//div[@class="sections-container"]//div[@class="section delivery-f2f"]')
        section_type['online'] = response.xpath('//div[@id="' + cid + '"]//div[@class="toggle-sections-link-container"]//div[@class="sections-container"]//div[@class="section delivery-online"]')
        section_type['blended'] = response.xpath('//div[@id="' + cid + '"]//div[@class="toggle-sections-link-container"]//div[@class="sections-container"]//div[@class="section delivery-blended"]')
        item = SectionItem()

        for types in section_type:
            sections = section_type[types]
            if sections:
                for section in sections:

                    item['cid'] = cid
                    item['sectionid'] = section.xpath('normalize-space(.//span[@class="section-id"]/text())').get()

                    if not section.xpath('.//span[@class="section-instructor"]/a/text()').get():
                        item['professor'] = section.xpath('normalize-space(.//span[@class="section-instructor"]/text())').get()
                    else:
                        item['professor'] = section.xpath('.//span[@class="section-instructor"]/a/text()').get()

                    item['totalseats'] = section.xpath('normalize-space(.//span[@class="total-seats-count"]/text())').get()
                    item['openseats'] = section.xpath('normalize-space(.//span[@class="open-seats-count"]/text())').get()

                    if len(section.xpath('.//span[@class="waitlist-count"]/text()').getall()) == 1:
                        item['waitlist'] = section.xpath('.//span[@class="waitlist-count"]/text()').get()
                        item['holdfile'] = None
                    else:
                        item['waitlist'] = section.xpath('.//span[@class="waitlist-count"]/text()').getall()[0]
                        item['holdfile'] = section.xpath('.//span[@class="waitlist-count"]/text()').getall()[1]

                    if types is 'f2f':
                        rows = section.xpath('.//div[@class="class-days-container"]//div[@class="row"]')

                        item['days'] = []
                        item['starttime'] = []
                        item['endtime'] = []
                        item['building'] = []
                        item['classroom'] = []
                        item['online'] = 0

                        for row in rows:
                            item['days'].append(row.xpath('.//span[@class="section-days"]/text()').get())
                            item['starttime'].append(row.xpath('.//span[@class="class-start-time"]/text()').get())
                            item['endtime'].append(row.xpath('.//span[@class="class-end-time"]/text()').get())

                            building = str(row.xpath('.//span[@class="building-code"]/text()').get())
                            if "TBA" in building:
                                item['building'].append(building)
                                item['classroom'].append("TBA")
                            else:
                                item['building'].append(building)
                                item['classroom'].append(row.xpath('.//span[@class="class-room"]/text()').get())

                        yield item

                    elif types is 'online':
                        rows = section.xpath('.//div[@class="class-days-container"]//div[@class="row"]')

                        item['days'] = []
                        item['starttime'] = []
                        item['endtime'] = []
                        item['building'] = []
                        item['classroom']=[]
                        item['online'] = 1

                        for row in rows:
                            if not section.xpath('.//div[@class="row"]//span[@class="section-days"]/text()').getall():
                                item['days'].append(None)
                                item['starttime'].append(None)
                                item['endtime'].append(None)
                                item['building'].append("ONLINE")
                                item['classroom'].append(row.xpath('.//span[@class="class-room"]/text()').get())
                            else:
                                item['days'].append(row.xpath('.//span[@class="section-days"]/text()').get())
                                item['starttime'].append(row.xpath('.//span[@class="class-start-time"]/text()').get())
                                item['endtime'].append(row.xpath('.//span[@class="class-end-time"]/text()').get())
                                item['building'].append("ONLINE")
                                item['classroom'].append(row.xpath('.//span[@class="class-room"]/text()').get())

                        yield item

                    elif types is 'blended':
                        rows = section.xpath('.//div[@class="class-days-container"]//div[@class="row"]')

                        item['days'] = []
                        item['starttime'] = []
                        item['endtime'] = []
                        item['building'] = []
                        item['classroom'] = []
                        item['online'] = 2

                        for row in rows:
                            if not row.xpath('.//span[@class="section-days"]/text()').getall():
                                item['days'].append(None)
                                item['starttime'].append(None)
                                item['endtime'].append(None)
                                item['building'].append("ONLINE")
                                item['classroom'].append(row.xpath('.//span[@class="class-room"]/text()').get())
                            else:
                                item['days'].append(row.xpath('.//span[@class="section-days"]/text()').get())
                                item['starttime'].append(row.xpath('.//span[@class="class-start-time"]/text()').get())
                                item['endtime'].append(row.xpath('.//span[@class="class-end-time"]/text()').get())

                                building = str(row.xpath('.//span[@class="building-code"]/text()').get())
                                if "TBA" in building:
                                    item['building'].append(building)
                                    item['classroom'].append("TBA")
                                else:
                                    item['building'].append(building)
                                    item['classroom'].append(row.xpath('.//span[@class="class-room"]/text()').get())

                        yield item





