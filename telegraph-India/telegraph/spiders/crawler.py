import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import os
from newspaper import Article
import pandas as pd 


class UrlsSpider(CrawlSpider):

    name = 'crawler'
    urls_dict = {}
    allowed_domains = ['www.telegraphindia.com']
    #tag = 'north-east'
    #tag = 'west-bengal'
    tag = 'india'
    cwd = os.getcwd().split('/')
    user_dir = '/'.join(cwd[:3]) 
    try:
        
        df = pd.read_csv('/home/ranu/repos/newspaper-crawling/telegraph-India/data/urls.csv')
        downloaded_articles = df.url.unique().tolist()
        print(f'The length of the urls downloaded is {len(downloaded_articles)}')
    except Exception as e:
        downloaded_articles = []
    start_urls = downloaded_articles
    root_dir = f'{user_dir}/repos/newspaper-crawling/telegraph/data/{tag}/'
    rules = (
        Rule(LinkExtractor(allow=f'{tag}'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        for i in response.xpath("//div/div[@class='col-8']/div[@class='row pb-3 pt-3']"):
            date = i.xpath(".//div[2]/div/span/text()").get()
            date = date.strip('Published ')
            url = i.xpath(".//div[2]/h2/a/@href").get()

            if url not in self.urls_dict:
                if response.urljoin(url) not in self.downloaded_articles:    
                    self.urls_dict[url] = response.urljoin(url)
                    yield scrapy.Request(url=response.urljoin(url),callback=self.parse_article,meta={'date':date})           

    def save_html(self, response):
        date = response.meta['date']
        root_dir = self.root_dir
        root_dir = root_dir + f'{date}'
        if not os.path.exists(root_dir):
            os.makedirs(root_dir)
        url = response.url
        full_url = response.urljoin(url)
        filename = full_url.replace('/','~')
        filename = f'{root_dir}/{filename}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)


    def parse_article(self, response):
        self.save_html(response)
        url = response.url
        full_url = response.urljoin(url)
        #self.log(f'Saved file {filename}')
        
        all_paras = []

        for i in response.xpath("//div[@class='fs-17 pt-2 noto-regular']/p"):
            para = i.xpath(".//text()").get()
            all_paras.append(para)
        
        full_text = ' '.join(all_paras)

        if full_text == '':
            article = Article(full_url)
            article.download()
            article.parse()
            full_text = article.text

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
            'article_url': full_url
        }
        yield dict_to_yield
