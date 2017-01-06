from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import Selector
from scrapy.http.request import Request
from northrop.items import NorthropItem
from scrapy.http import HtmlResponse
from scrapy.exceptions import CloseSpider
import re

class NorthropSpider(CrawlSpider):
  name = "northropJobStart"
  
  start_urls = ['https://ngc.taleo.net/careersection/ngc_pro/jobsearch.ftl?lang=en#']
  allowed_domains = ["ngc.taleo.net"]

  rules = (
        Rule(LinkExtractor(allow=(), restrict_xpaths=('//*[@id="next"]/a',)), callback="parse_listings", follow= True),
  )

  def parse_start_url(self, response):
    return self.parse_listings(response)

  def parse_listings(self, response):
    sel = Selector(response)
    jobs = sel.xpath('//th/div/div/span/a/@href').extract()
    for job_url in jobs:
      job_url = self.__normalise(job_url)
      job_url = self.__to_absolute_url(response.url,job_url)
      yield Request(job_url, callback=self.parse_details)

  def parse_details(self, response):
    sel = Selector(response)
    job = sel.xpath('//*[@id="mainbody-jobs"]')
    item = NorthropItem()
    # Populate job fields
    item['title'] = job.xpath('//*[@id="mainbody-jobs"]/h1/text()').extract()
    item['location'] = job.xpath('//*[@id="mainbody-jobs"]/div[3]/div[2]/div[1]/div/div[3]/div[2]/text()').extract()
    item['applink'] = job.xpath('//*[@id="mainbody-jobs"]/div[3]/div[1]/a/@href').extract()
    item['description'] = job.xpath('//*[@id="mainbody-jobs"]/div[3]/div[2]/div[2]/div[1]/div[2]').extract()
    item['travel'] = job.xpath('//*[@id="mainbody-jobs"]/div[3]/div[2]/div[1]/div/div[5]/div[2]/text()').extract()
    item['job_category'] = job.xpath('//*[@id="mainbody-jobs"]/div[3]/div[2]/div[1]/div/div[2]/div[2]/text()').extract()
    item['clearance_have'] = job.xpath('//*[@id="mainbody-jobs"]/div[3]/div[2]/div[1]/div/div[8]/div[2]/text()').extract()
    item['clearance_get'] = job.xpath('//*[@id="mainbody-jobs"]/div[3]/div[2]/div[1]/div/div[8]/div[2]/text()').extract()
    item['job_number'] = job.xpath('//*[@id="mainbody-jobs"]/div[3]/div[2]/div[1]/div/div[1]/div[2]/text()').extract()
    item['page_url'] = response.url
    item = self.__normalise_item(item, response.url)
    return item



  def __normalise_item(self, item, base_url):
    '''
    Standardise and format item fields
    '''
    # Loop item fields to sanitise data and standardise data types
    for key, value in vars(item).values()[0].iteritems():
      item[key] = self.__normalise(item[key])
      # Convert job URL from relative to absolute URL
      #item['job_url'] = self.__to_absolute_url(base_url, item['job_url'])
      return item

  def __normalise(self, value):
    # Convert list to string
    value = value if type(value) is not list else ' '.join(value)
    # Trim leading and trailing special characters (Whitespaces, newlines, spaces, tabs, carriage returns)
    value = value.strip()
    return value

  def __to_absolute_url(self, base_url, link):
    '''
    Convert relative URL to absolute URL
    '''
    import urlparse
    link = urlparse.urljoin(base_url, link)
    return link

  def __to_int(self, value):
    '''
    Convert value to integer type
    '''
    try:
      value = int(value)
    except ValueError:
      value = 0
    return value

  def __to_float(self, value):
    '''
    Convert value to float type
    '''
    try:
      value = float(value)
    except ValueError:
      value = 0.0
    return value
