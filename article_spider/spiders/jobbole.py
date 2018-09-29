# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse


class JobboleSpider(scrapy.Spider):
    name = "jobbole"
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):

        post_nodes = response.css('#archive .floated-thumb .post-thumb a')
        for post_node in post_nodes:
            image_url = post_node.css('img::attr(src)').extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url),meta={"front_image_url": image_url}, callback=self.parse_detail)

        next_url = response.css('.next.page-numbers::attr("href")').extract_first('')
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        # 提取文章的具体字段
        title = response.xpath('//*[@id="post-110287"]/div[1]/h1/text()').extract_first('')
        create_time = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract_first(
            '').strip().replace(
            "·", " ").strip()
        praise_nums = response.xpath('//span[contains(@class,"vote-post-up")]//h10/text()').extract_first('')
        fav_nums = response.xpath('//span[contains(@class,"bookmark-btn")]/text()').extract_first('')
        fav_match = re.match(".*?(\d+)", fav_nums)
        if fav_match:
            fav_nums = fav_match.group(1)
        comments_nums = response.xpath('//a[@href="#article-comment"]/span/text()').extract_first('')
        comments_match = re.match(".*?(\d+)", comments_nums)
        if comments_match:
            comments_nums = comments_match.group(1)
        tag_list = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        tag_list = [element for element in tag_list if not element.strip().endswith('评论')]
        tags = ",".join(tag_list)
