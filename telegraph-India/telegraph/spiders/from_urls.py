# -*- coding: utf-8 -*-
import scrapy
import pandas as pd 
from newsfetch.news import newspaper


class FromUrlsSpider(scrapy.Spider):
    name = 'from_urls'
    allowed_domains = ['www.telegraphindia.com']

    df = pd.read_parquet('/home/ranu/repos/newspaper-crawling/data/india.parquet')
    urls_list = df.article_url.unique().tolist()
    start_urls = urls_list
    
    def parse(self,response):
        url = response.url
        full_url = response.urljoin(url)
        news = newspaper(full_url)
        
        dict_to_return = news.get_dict
        all_paras = []

        for i in response.xpath("//div[@class='fs-17 pt-2 noto-regular']/p"):
            para = i.xpath(".//text()").get()
            all_paras.append(para)
            
        tags_list = []
        for i in response.xpath("//div[@class='pb-3 text-center fs-12 uk-text-69 noto-regular listed_topics']/a"):
            tag = i.xpath(".//text()").get()
            tags_list.append(tag)

        
        full_text = ' \n'.join(all_paras)
        
        dict_to_return['text_by_para'] = full_text
        
        dict_to_return['tags_list'] = tags_list
        
        yield dict_to_return
