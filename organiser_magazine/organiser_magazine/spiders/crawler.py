import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import os
from newspaper import Article
import pandas as pd 

class CrawlerSpider(CrawlSpider):
    name = 'crawler'
    tag = 'Polity'
    allowed_domains = ['www.organiser.org']
    #start_urls = [f'https://www.organiser.org/{tag}.html']
    start_urls = ['https://www.organiser.org/Polity.html']
    cwd = os.getcwd().split('/')
    user_dir = '/'.join(cwd[:3]) 
    root_dir = f'{user_dir}/repos/newspaper-crawling/organiser_magazine/data/{tag}/'
    rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        urls_dict = {}
        for i in response.xpath("//div[@style='text-align:right']/a"):
            url = i.xpath(".//@href").get()
            self.log(url)
            if url not in urls_dict:
                urls_dict[url] = url
                yield scrapy.Request(url=url, callback=self.parse_article)

    def save_html(self, response):
        root_dir = self.root_dir
        if not os.path.exists(root_dir):
            os.makedirs(root_dir)
        url = response.url
        filename = url.replace('/','~')
        filename = f'{root_dir}/{filename}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)  
 
    def parse_article(self,response):

        self.save_html(response)
        url = response.url
        self.log(f'The url of this page is {url}')
        title = response.xpath("//div[@class='heading_container']/h1/text()").get()
        author_name = response.xpath("//div[@class='body_container']/div[@style='text-align: right; ']/strong/text()").get()
        publication_date = response.xpath("//div[@class='date_and_author_container']/span[1]/text()[2]").get()
        full_text = []
        for i in response.xpath("//div[@class='body_container']/div"):
            text = i.xpath(".//text()").get()
            if text != author_name:
                try:
                    if len(text) > 5:
                        full_text.append(text)
                except:
                    print("")
        if len(full_text) > 0:
            full_text = ' '.join(full_text)

        yield {
            'title':title,
            'publication_date':publication_date,
            'author_name': author_name,
            'full_text':full_text,
            'article_url':url
        }