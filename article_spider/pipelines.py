# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import pymysql
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi
from django.db import models

class ArticleSpiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding='utf-8')
        self.file.write('[')

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + ",\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.write(']')
        self.file.close()


class JsonExporterPipleline(object):
    def __init__(self):
        self.file = open('articleexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class MysqlPipeline(object):
    def __init__(self):
        self.conn = pymysql.connect('47.96.143.96', user="hzy9738", password="hong9738", db="jobbole_article",
                                    port=3306)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into article(title, url, url_object_id, create_date, fav_nums) 
            VALUES (%s, %s, %s, %s, %s)
        """
        self.cursor.execute(insert_sql,
                            (item['title'], item['url'], item['url_object_id'], item['create_date'], item['fav_nums']))
        self.conn.commit()


class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dpparms = dict(
            host=settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            password = settings["MYSQL_PASSWORD"],
            charset = 'utf8',
            cursorclass = pymysql.cursors.DictCursor,
            use_unicode= True
        )
        dppool = adbapi.ConnectionPool("pymysql", **dpparms)
        return  cls(dppool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)

    def handle_error(self, failure):
        print( failure )

    def do_insert(self, cursor, item):
         insert_sql = """
            insert into article(title, url, url_object_id, create_date, fav_nums)
            VALUES (%s, %s, %s, %s, %s)
         """
         cursor.execute(insert_sql,
                    (item['title'], item['url'], item['url_object_id'], item['create_date'], item['fav_nums']))




class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        for ok, value in results:
            image_file_path = value['path']

        item['front_image_path'] = image_file_path

        return item
