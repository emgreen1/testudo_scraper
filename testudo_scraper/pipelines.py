#logging to keep track of important information
#import the model being used and send the formatted items to their respective
#models

import logging
import django
from django.db import connection
from testudo.models import Departments

from .items import DepartmentItem, ClassItem, SectionItem

def item_type(item):
    return str(type(item)).split("'")[1].split(".")[3]

def time_convert(time):
    if "pm" in time:
        time = time[:-2]
        if '12' in time:
            time += ':00'
            return time
        if len(time) == 4: 
            time = '0' + time
            time = str(int(time[:2]) + 12) + time[2:] + ':00'
            return time
        else:
            time = str(int(time[:2]) + 12) + time[2:] + ':00'
            return time
    if "am" in time:
        time = time[:-2]
        if len(time) == 4: 
            time = '0' + time + ':00'
            return time
        else: 
            time += ':00'
            return time


class TestudoScraperPipeline:
    def process_item(self, item, spider): 
        itemType = item_type(item)
        logging.log(logging.INFO, "Item type: {}".format(itemType))
        
        if isinstance(item, DepartmentItem):
            #================= DEPARTMENTS MODEL ========================
            logging.log(logging.INFO, "Item abrev: {}".format(item['dept_abrev']))
            abrev = str(item['dept_abrev'])
            
            logging.log(logging.INFO, "Item term: {}".format(item['dept_abrev_term']))
            term = str(item['dept_abrev_term'])

            logging.log(logging.INFO, "Item name: {}".format(item['dept_name']))
            name = str(item['dept_name'])

            query = """INSERT INTO departments (dept_abrev, dept_name, dept_abrev_term)
                    VALUES(\"{}\", \"{}\", \"{}\")
                    ON DUPLICATE KEY UPDATE dept_abrev=\"{}\", dept_name=\"{}\", dept_abrev_term=\"{}\"
                    """.format(abrev, name, term, abrev, name, term)
        
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
            logging.log(logging.INFO, """Item {} successfully
                                   uploaded into departments
                                   at row {}
                                   """.format(str(item['dept_abrev']), cursor.rowcount))
            cursor.close()
        
        if isinstance(item, ClassItem):
            #================ CLASSES MODEL ===========================
            logging.log(logging.INFO, "Item cid: {}".format(item['cid']))
            cid = str(item['cid'])

            logging.log(logging.INFO, "Item term: {}".format(item['dept_abrev_term']))
            term = str(item['dept_abrev_term'])

            logging.log(logging.INFO, "Item title: {}".format(item['title']))
            title = str(item['title']).replace("\"", "'")

            logging.log(logging.INFO, "Item min: {}".format(item['mincredits']))
            if item['mincredits'] is not None:
                mincreds = int(item['mincredits'])
            else: 
                mincreds = 0

            logging.log(logging.INFO, "Item max: {}".format(item['maxcredits']))
            if item['maxcredits'] is not None:
                maxcreds = int(item['maxcredits'])
            else:
                maxcreds = 0

            logging.log(logging.INFO, "Item descrip: {}".format(item['descrip']))
            descrip = str(item['descrip']).replace("\"", "'")

            query1 = """INSERT INTO classes (class_id, class_title, min_credits, max_credits, class_descr, dept_abrev_term_id) 
                        VALUES (\"{}\", \"{}\", \"{}\", \"{}\", \"{}\", \"{}\") 
                        ON DUPLICATE KEY UPDATE class_id=\"{}\", class_title=\"{}\", min_credits=\"{}\", max_credits=\"{}\", class_descr=\"{}\", dept_abrev_term_id=\"{}\"
                        """.format(cid, title, mincreds, maxcreds, descrip, term, cid, title, mincreds, maxcreds, descrip, term)

            cursor = connection.cursor()
            cursor.execute(query1)
            connection.commit()
            logging.log(logging.INFO, "Item {} successfully uploaded into classes table at row {}".format(cid, cursor.rowcount))
            cursor.close()
            
            if item['geneds'] is not None:
                for geneds in item['geneds']:
                    gened = str(geneds)
                    logging.log(logging.INFO, "Item geneds: {}".format(gened))

                    class_gen = cid + '-' + gened
                    query2 = """INSERT INTO geneds (gen_ed, class_gen, class_id_id)
                                VALUES (\"{}\", \"{}\", \"{}\")
                                ON DUPLICATE KEY UPDATE gen_ed=\"{}\", class_gen=\"{}\", class_id_id=\"{}\"
                                """.format(gened, class_gen, cid, gened, class_gen, cid)
                    
                    cursor = connection.cursor()
                    cursor.execute(query2)
                    connection.commit()
                    logging.log(logging.INFO, "Item {} successfully uploaded into geneds table at row {}".format(cid, cursor.rowcount))


        if isinstance(item, SectionItem):
            #=========================== SECTIONS MODEL ======================
            logging.log(logging.INFO, "Item cid: {}".format(item['cid']))
            cid = str(item['cid'])

            logging.log(logging.INFO, "Item section: {}".format(item['sectionid']))
            section = cid + '-' +  str(item['sectionid'])

            logging.log(logging.INFO, "Item prof: {}".format(item['professor']))
            prof = str(item['professor'])

            logging.log(logging.INFO, "Item total: {}".format(item['totalseats']))
            total = int(item['totalseats'])

            logging.log(logging.INFO, "Item open: {}".format(item['openseats']))
            opens = int(item['openseats'])

            logging.log(logging.INFO, "Item wait: {}".format(item['waitlist']))
            wait = int(item['waitlist'])

            logging.log(logging.INFO, "Item hold: {}".format(item['holdfile']))
            if item['holdfile'] is not None:
                hold = int(item['holdfile'])
            else:
                hold = 0

            logging.log(logging.INFO, "Item online: {}".format(item['online']))
            online = int(item['online'])

            query1 = """INSERT INTO sections (section_id, professor, total_seats, open_seats, waitlist, holdfile, online, class_id_id)
                            VALUES (\"{}\", \"{}\", \"{}\", \"{}\", \"{}\", \"{}\", \"{}\", \"{}\")
                            ON DUPLICATE KEY UPDATE section_id=\"{}\", professor=\"{}\", total_seats=\"{}\", open_seats=\"{}\", waitlist=\"{}\", holdfile=\"{}\", online=\"{}\", class_id_id=\"{}\"
                            """.format(section, prof, total, opens, wait, hold, online, cid, section, prof, total, opens, wait, hold, online, cid)


            cursor = connection.cursor()
            cursor.execute(query1)
            connection.commit()
            logging.log(logging.INFO, "Item {} successfully uploaded into sections table at row {}".format(section, cursor.rowcount))
            cursor.close()

            #======================= DAYS MODEL ================================
            days = item['days']
            i = 0
            logging.log(logging.INFO, "BUILDING AND CLASSROOM: {} {}".format(item['building'], item['classroom']))
            for day in days:
                if day is not None:
                    logging.log(logging.INFO, "Item section_id: {}".format(section))

                    logging.log(logging.INFO, "Item day: {}".format(day))

                    start = time_convert(str(item['starttime'][i]))
                    if start is None:
                        start = "00:00:00"
                    logging.log(logging.INFO, "Item start: {}".format(start))

                    end = time_convert(str(item['endtime'][i]))
                    if end is None:
                        end = "00:00:00"
                    logging.log(logging.INFO, "Item end: {}".format(end))

                    build = str(item['building'][i])
                    logging.log(logging.INFO, "Item building: {}".format(build))

                    class_ = str(item['classroom'][i])
                    logging.log(logging.INFO, "Item class: {}".format(class_))

                    section_day = section + '-' + day;

                    query = """INSERT INTO Days (days, start_time, end_time, building, classroom, section_day, section_id_id)
                            VALUES (\"{}\", \"{}\", \"{}\", \"{}\", \"{}\", \"{}\", \"{}\")
                            ON DUPLICATE KEY UPDATE days=\"{}\", start_time=\"{}\", end_time=\"{}\", building=\"{}\", classroom=\"{}\", section_day=\"{}\", section_id_id=\"{}\"
                            """.format(day, start, end, build, class_, section_day, section, day, start, end, build, class_, section_day, section)
                    i += 1

                    cursor = connection.cursor()
                    cursor.execute(query)
                    connection.commit()
                    logging.log(logging.INFO, "Item {} successfully uploaded into days table at row {}".format(section, cursor.rowcount))
                    cursor.close()
                else:
                    i += 1


        return item
