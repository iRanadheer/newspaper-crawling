import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import os
from newspaper import Article
import pandas as pd 
import numpy as np 

class CrawlerSpider(CrawlSpider):
    name = 'crawler'
    tag = 'Polity'
    allowed_domains = ['www.organiser.org']
    #start_urls = [f'https://www.organiser.org/{tag}.html']
    start_urls = ['https://www.organiser.org/Polity.html']
    cwd = os.getcwd().split('/')
    user_dir = '/'.join(cwd[:3]) 
    root_dir = f'{user_dir}/repos/newspaper-crawling/organiser_magazine/data/{tag}/'

    try:
        
        downloaded_articles = pd.read_csv(f'{user_dir}/repos/newspaper-crawling/organiser_magazine/data/organiser_content.csv')
        downloaded_articles = downloaded_articles.article_url.tolist()
        print(f'The length of the urls downloaded is {len(downloaded_articles)}')
    except Exception as e:
        downloaded_articles = []

    rules = (
        Rule(LinkExtractor(deny='/archives/'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        urls_dict = {}
        for i in response.xpath("//div[@style='text-align:right']/a"):
            url = i.xpath(".//@href").get()
            self.log(url)
            if url not in self.downloaded_articles:    
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

        # The html structure is different for different article
        # So, capturing all elements with a generic code can be difficult. So,
        # we have randomly selected few articles and checked their selectors and develeped this code.
        # This maynot give us 100% output, but somehere arouond 
        title = response.xpath("//div[@class='heading_container']/h1/text()").get()
        if title == np.nan:
            title = response.xpath("//div[@class='heading clsNewsTitleHeading1']/text()").get()

        author_name = response.xpath("//div[@class='body_container']/div[@style='text-align: right; ']/strong/text()").get()

        if author_name == np.nan:
            author_name = response.xpath("//div/h4/text()").get()
    
        year = url.split('/')[5]
        month = url.split('/')[6]
        date = url.split('/')[7]

        publication_date = str(date) + '-' + str(month) + '-' + str(year)

        full_text = []
        for i in response.xpath("//div[@class='body_container']/div"):
            text = i.xpath(".//text()").get()
            if text != author_name:
                try:
                    if len(text) > 5:
                        full_text.append(text)
                except:
                    print("")

        if len(full_text) == 0:
            for i in response.xpath("//div[@class='newscontent']/div[13]/div"):
                text = i.xpath(".//text()").get()
                if len(text) != 0:
                    full_text.append(text)

        if len(full_text) == 0:
            for i in response.xpath("//div[@class='newscontent']/div[9]/div"):
                text = i.xpath(".//text()").get()
                if len(text) != 0:
                    full_text.append(text)

        if len(full_text) == 0:
            for i in response.xpath("//div[@class='newscontent']/div"):
                text = i.xpath(".//text()").get()
                if len(text) != 0:
                    full_text.append(text)

        if len(full_text) == 0:
            for i in response.xpath("//div[@class='body_container']/span/div[3]/div"):
                text = i.xpath(".//text()").get()
                if len(text) != 0:
                    full_text.append(text)

        if len(full_text) == 0:
            for i in response.xpath("//div[@class='body_container']/span/div"):
                text = i.xpath(".//text()").get()
                if len(text) != 0:
                    full_text.append(text)

        if len(full_text) == 0:
            for i in response.xpath("//div[@class='body_container']/span/h3/span/div"):
                text = i.xpath(".//text()").get()
                if len(text) != 0:
                    full_text.append(text)

        if len(full_text) == 0:
            for i in response.xpath("//div[@class='body_container']/div/div"):
                text = i.xpath(".//text()").get()
                if len(text) != 0:
                    full_text.append(text)

        if len(full_text) > 0:
            full_text = ' '.join(full_text)


        tags_list = []
        for i in response.xpath("//div[@class='tagcloud02']/div[2]/ul/li"):
            text = i.xpath(".//text()").get()
            if text != np.nan:
                tags_list.append(text)


        yield {
            'title':title,
            'publication_date':publication_date,
            'author_name': author_name,
            'tags_list' : tags_list,
            'full_text':full_text,
            'article_url':url
        }