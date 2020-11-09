import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class TestSpider(CrawlSpider):
    name = 'test'
    allowed_domains = ['www.organiser.org']
    tag = 'Polity'
    #start_urls = [f'https://www.organiser.org/{tag}.html']
    start_urls = ['https://www.organiser.org/Polity.html']
    root_dir = f'~/repos/newspaper-crawling/organiser-magazine/data/{tag}/'
    rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )
    def parse_item(self, response):
        urls_dict = {}
        for i in response.xpath("//div[@style='text-align:right']/a"):
            url = i.xpath(".//@href").get()
            self.log(url)
            yield {
                'url':url
            }
