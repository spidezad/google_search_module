'''

#############################################

 Module to get google search results by using Scrapy (Spider module)
 Author: Tan Kok Hua (Guohua tan)
 Email: spider123@gmail.com
 Revised date: Apr 11 2014

##############################################

Scrapy Spider Module to
    1) Scrape the google link results from the google search page
    2) Scrape the individual links for the title and description.

Updates:
    Apr 17 2014: Cater for mutliple google search
    Apr 12 2014: Resolve issues with unrecognise character
                : Add in join_list_of_str function and remove_whitespace_fr_raw
                : Add in paragraph process
                : Add in option to extract text from paragraph

TODO: Enable injecting of some tag for xml collection

'''

import re
import os
import sys
import json
import string
import yaml
from scrapy.spider import Spider
from scrapy.selector import Selector
from Python_Google_Search import gsearch_url_form_class 

# Options
GS_LINK_JSON_FILE       = r'C:\data\temp\output'
RESULT_FILE             = r'c:\data\temp\htmlread_1.txt'

ENABLE_TEXT_SUMMARIZE   = 0 # For NLTK to look into the text for details.
ENABLE_PARAGRAPH_STORED = 1 # Store website content to file.

class GoogleSearch(Spider):

    # Save the result file: Always in the same file
    # re -start at each section of the run
    with open(RESULT_FILE,'w') as f:
        f.write('')
        print 'Restart the log file'

    with open(GS_LINK_JSON_FILE,'w') as f:
        f.write('')
        print 'Restart the GS_LINK_JSON_FILE file'

    # for retrieving the settings from json file
    search_class = gsearch_url_form_class("")
    setting_data = search_class.retrieved_setting_fr_json_file()

    # Parameters set used for spider crawling
    name = setting_data['Name']
    allowed_domains = setting_data['Domain']
    start_urls = setting_data['SearchUrl']

    def join_list_of_str(self,list_of_str, joined_chars= '...'):
        '''
            Function to combine a list of str to one long str
            list of str --> str

        '''
        return joined_chars.join([n for n in list_of_str])

    def remove_whitespace_fr_raw(self,raw_input):
        '''
            Remove unnecessary white space such as \r,\t,\n
            str raw_input --> str
            
        '''
        
        for n in ['\n','\t','\r']:
            raw_input = raw_input.replace(n,'')
        return raw_input

    def combine_all_url_link_for_multiple_search(self,more_url_list):
        '''
            Combine all the url link list in the event of mutliple search.
            list more_url_list --> none
            get from Json file and eventually dump all back
        '''
        
        with open(GS_LINK_JSON_FILE, "r") as outfile:
            setting_data = yaml.load(outfile)

        if setting_data is None or not setting_data.has_key('output_url'):
            setting_data = dict()
            setting_data['output_url'] = []

        with open(GS_LINK_JSON_FILE, "w") as outfile:
            json.dump({'output_url': setting_data['output_url']+more_url_list}, outfile, indent=4)
        


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
            self.combine_all_url_link_for_multiple_search(google_search_links_list)

        if self.setting_data['type_of_parse'] == 'general':

            print 
            print 'general website processing'
            sel = Selector(response)

            ## Get meta info from website
            title = sel.xpath('//title/text()').extract()
            if len(title)>0:
                title = title[0].encode(errors='replace') #replace any unknown character with ?
            contents = sel.xpath('/html/head/meta[@name="description"]/@content').extract()
            if len(contents)>0:
                contents = contents[0].encode(errors='replace') #replace any unknown character with ?

            if ENABLE_PARAGRAPH_STORED:
                paragraph_list = sel.xpath('//p/text()').extract()
                para_str = self.join_list_of_str(paragraph_list, joined_chars= '..')
                para_str = para_str.encode(errors='replace')
                para_str = self.remove_whitespace_fr_raw(para_str)
                

            print
            print title
            print 
            print contents

            ## Dump results to text file
            with open(RESULT_FILE,'a') as f:
                f.write('\n')
                f.write('#'*20)
                f.write('\n')
                f.write(title + '\n')
                f.write(response.url)
                for n in range(2): f.write('\n')
                f.write(str(contents))
                for n in range(2): f.write('\n')
                if ENABLE_PARAGRAPH_STORED:
                    f.write(para_str)
                f.write('\n')
                f.write('#'*20)
                for n in range(2): f.write('\n')

        print
        print 'Completed'








