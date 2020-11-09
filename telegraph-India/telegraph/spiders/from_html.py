# -*- coding: utf-8 -*-
import scrapy
import pandas as pd 
from newsfetch.news import newspaper
from glob import glob


class FromUrlsSpider(scrapy.Spider):
    name = 'from_html'
    allowed_domains = ['www.telegraphindia.com']

    #df = pd.read_parquet('/home/ranu/repos/newspaper-crawling/data/india.parquet')
    #urls_list = df.article_url.unique().tolist()
    all_html = glob('/home/ranu/learning/scrapy-tutorials/telegraph/data/india/*/*.html')
    all_html = [('file://' + i) for i in all_html]

    start_urls = all_html
    
    def parse(self,response):
        url  = response.url 
        all_paras = []

        for i in response.xpath("//div[@class='fs-17 pt-2 noto-regular']/p"):
            para = i.xpath(".//text()").get()
            all_paras.append(para)
        
        full_text = '\n '.join(all_paras)

        author_name = response.xpath("//div[@class='uk-text-69 pt-2 pb-2 overflow-auto noto-regular']/div/a/span[@class='text-breadcrumbs']/text()").get()
        author_name = author_name.strip()
        publication_place = response.xpath("//div[@class='uk-text-69 pt-2 pb-2 overflow-auto noto-regular']/div/a[@class='muted-link'][2]/span/text()").get()
        publication_date = response.xpath("//div[@class='fs-12 float-left']/span/text()").get()

        tags_list = []
        for i in response.xpath("//div[@class='pb-3 text-center fs-12 uk-text-69 noto-regular listed_topics']/a"):
            tag = i.xpath(".//text()").get()
            tags_list.append(tag)

        title = response.xpath("//h1[@class='fs-45 uk-text-1D noto-bold mb-2']/text()[2]").get()
        title = title.strip()
        sub_title = response.xpath("//div[@class='fs-20 uk-text-69 noto-regular']/text()").get()
        sub_title = sub_title.strip()

        dict_to_yield = {
            'title' : title,
            'sub_title': sub_title,
            'author_name' : author_name,
            'publication_place': publication_place,
            'publication_date': publication_date,
            'full_text' : full_text,
            'tags_list': tags_list,
            'article_url': url
        }
        yield dict_to_yield
