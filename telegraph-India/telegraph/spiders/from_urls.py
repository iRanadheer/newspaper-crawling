# -*- coding: utf-8 -*-
import scrapy
import pandas as pd 
from newsfetch.news import newspaper


class FromUrlsSpider(scrapy.Spider):
    name = 'from_urls'
    allowed_domains = ['www.telegraphindia.com']

    df = pd.read_parquet('/home/ranu/repos/newspaper-crawling/telegraph-India/data/india.parquet')
    urls_list = df.article_url.unique().tolist()
    start_urls = urls_list
    
    def parse(self,response):
        url = response.url
        full_url = response.urljoin(url)
        news = newspaper(full_url)
            #dataframe = pd.DataFrame.from_dict(news.get_dict, orient='index')
            ##dataframe = dataframe.transpose()

        yield news.get_dict
