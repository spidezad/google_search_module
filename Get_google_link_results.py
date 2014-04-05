'''

#############################################

 Module to get google search results by using Scrapy (Spider module)
 Author: Tan Kok Hua (Guohua tan)
 Email: spider123@gmail.com
 Revised date: Apr 05 2014

##############################################

    Scrapy Spider Module to
    1) Scrape the google link results from the google search page
    2) Scrape the individual links for the title and description.

'''

import re
import os
import sys
import json
from scrapy.spider import Spider
from scrapy.selector import Selector
from Python_Google_Search import gsearch_url_form_class 

GS_LINK_JSON_FILE = r'C:\data\temp\output'
RESULT_FILE = r'c:\data\temp\htmlread_1.txt'

class GoogleSearch(Spider):

    # Save the result file: Always in the same file
    # re -start at each section of the run
    with open(RESULT_FILE,'w') as f:
        f.write('')
        print 'Restart the log file'

    # for retrieving the settings from json file
    search_class = gsearch_url_form_class("")
    setting_data = search_class.retrieved_setting_fr_json_file()

    # Parameters set used for spider crawling
    name = setting_data['Name']
    allowed_domains = setting_data['Domain']
    start_urls = setting_data['SearchUrl']

    def parse(self, response):
        '''
           Required function for spider to crawl
           Run two different type of parsing depending on the json keyword type of parse
               if type of parse == google_search --> get list of links from google results
               if type of parse == general --> get the meta information for each site
        '''

        if self.setting_data['type_of_parse'] == 'google_search':
            print
            print 'For google search parsing'
            
            ## Get the selector for xpath parsing
            sel = Selector(response)
            google_search_links_list =  sel.xpath('//h3/a/@href').extract()
            google_search_links_list = [re.search('q=(.*)&sa',n).group(1) for n in google_search_links_list if re.search('q=(.*)&sa',n)]

            ## Display a list of the result link
            for n in google_search_links_list:
                print n

            ## Dump all results to file
            with open(GS_LINK_JSON_FILE, "w") as outfile:
                json.dump({'output_url':google_search_links_list}, outfile, indent=4)

        if self.setting_data['type_of_parse'] == 'general':

            print 
            print 'general website processing'
            sel = Selector(response)

            ## Get meta info from website
            title = sel.xpath('//title/text()').extract()
            if len(title)>0: title = title[0]
            contents = sel.xpath('/html/head/meta[@name="description"]/@content').extract()
            if len(contents)>0: contents = contents[0]

            print
            print title
            print 
            print contents

            ## Dump results to text file
            with open(RESULT_FILE,'a') as f:
                f.write(title + '\n')
                f.write(response.url)
                for n in range(2): f.write('\n')
                f.write(str(contents))
                for n in range(2): f.write('\n')
                f.write('#'*20)
                for n in range(2): f.write('\n')
                print
                print 'Write all data to file'

        print
        print 'Completed'








