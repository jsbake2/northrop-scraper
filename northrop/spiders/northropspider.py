import json
import scrapy
from scrapy.http.request import Request
from scrapy.selector import Selector
from northrop.items import NorthropItem


class NorthropSpider(scrapy.Spider):
    name = 'northropJobStart'
    start_urls = ['https://ngc.taleo.net/careersection/ngc_pro/jobsearch.ftl?lang=en#']
    # baseform with base search values
    base_form = {'advancedSearchFiltersSelectionParam':
        {'searchFilterSelections': [
            {'id': 'ORGANIZATION', 'selectedValues': []},
            {'id': 'LOCATION', 'selectedValues': []},
            {'id': 'JOB_FIELD', 'selectedValues': []},
            {'id': 'URGENT_JOB', 'selectedValues': []},
            {'id': 'EMPLOYEE_STATUS', 'selectedValues': []},
            {'id': 'STUDY_LEVEL', 'selectedValues': []},
            {'id': 'WILL_TRAVEL', 'selectedValues': []},
            {'id': 'JOB_SHIFT', 'selectedValues': []},
            {'id': 'JOB_NUMBER', 'selectedValues': []}]},
        'fieldData': {'fields': {'JOB_TITLE': '', 'KEYWORD': '', 'LOCATION': ''},
                      'valid': True},
        'filterSelectionParam': {'searchFilterSelections': [{'id': 'POSTING_DATE',
                                                             'selectedValues': []},
                                                            {'id': 'LOCATION', 'selectedValues': []},
                                                            {'id': 'JOB_FIELD', 'selectedValues': []},
                                                            {'id': 'JOB_TYPE', 'selectedValues': []},
                                                            {'id': 'JOB_SCHEDULE', 'selectedValues': []},
                                                            {'id': 'JOB_LEVEL', 'selectedValues': []}]},
        'multilineEnabled': False,
        'pageNo': 1,  # <--- change this for pagination
        'sortingSelection': {'ascendingSortingOrder': 'false',
                             'sortBySelectionParam': '3'}}


    def parse_details(self, response):
      sel = Selector(response)
      job = sel.xpath('//*[@id="ngc-career"]')
      item = NorthropItem()
      # Populate job fields
      item['description'] = job.xpath('//*[@id="initialHistory"]').extract()
      item['page_url'] = response.url

      return item


    def parse(self, response):
        # we got cookies from first start url now lets request into the search api
        # copy base form for the first request
        form = self.base_form.copy()
        yield scrapy.Request('https://ngc.taleo.net/careersection/rest/jobboard/searchjobs?lang=en&portal=2160420105',
                             body=json.dumps(self.base_form),
                             # add headers to indicate we are sending a json package
                             headers={'Content-Type': 'application/json',
                                      'X-Requested-With': 'XMLHttpRequest'},
                             # scrapy.Request defaults to 'GET', but we want 'POST' here
                             method='POST',
                             # load our form into meta so we can reuse it later
                             meta={'form': form},
                             callback=self.parse_items)

    def parse_items(self, response):
        data = json.loads(response.body)
        # scrape data
        for item in data['requisitionList']:
            yield Request(url='https://ngc.taleo.net/careersection/ngc_pro/jobdetail.ftl?job='+item[u'jobId'], callback=self.parse_details)
            #yield item

        # next page
        # get our form back and update the page number in it
        form = response.meta['form']
        form['pageNo'] += 1
        # check if paging is over, is our next page higher than maximum page?
        max_page = data['pagingData']['totalCount'] / data['pagingData']['pageSize']
        if form['pageNo'] > max_page:
            return
        yield scrapy.Request('https://ngc.taleo.net/careersection/rest/jobboard/searchjobs?lang=en&portal=2160420105',
                             body=json.dumps(form),
                             headers={'Content-Type': 'application/json',
                                      'X-Requested-With': 'XMLHttpRequest'},
                             method='POST',
                             meta={'form': form},
                             callback=self.parse_items)