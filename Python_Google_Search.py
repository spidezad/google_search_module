'''
#############################################

 Module to get google search results by using Scrapy
 Author: Tan Kok Hua (Guohua tan)
 Email: spider123@gmail.com
 Revised date: Apr 011 2014

##############################################

Usage:
    Retrieve the google results links from google search site using Scrapy
    For each link, use scrapy to crawl the title and contents.
    By minimizing the information retrieved from the google search site, allows more independent control of info extract
    and also reduce the dependency on google format/tag change.

    Uses the windows platform. called the scrapy crawler from command line.

Required Modules:
    YAML --> for the clean html, resolve unicode.
    Scrapy --> for scraping website, make use of scrapy crawler

Updates:
    Apr 16 2014: re arrange the self.reformat_search_for_spaces function tot formed_individual_url function
               : Add in capability to handle multiple search items
    Apr 11 2014: Add in users parameters
    Apr 09 2014: Add in modify_search_key function

TODO:
    Add in advanced google search
    http://www.johntedesco.net/blog/2012/06/21/how-to-solve-impossible-problems-daniel-russells-awesome-google-search-techniques/
    expand to multiple keyword search

'''

import re
import os
import sys
import json

import yaml
from scrapy.spider import Spider
from scrapy.selector import Selector


class gsearch_url_form_class(object):
    '''
        class for forming the url to be used in search
        The following is temp format for google search
    '''
    def __init__(self, google_search_keyword = '' ):
        '''
            Take in the search key word and transform it to the google search url
            str/list google_search_keyword --> None
            Able to take in a list or str,
                if str will set to self.g_search_key
                else set to self.g_search_key_list


            #need to add the search item

            #ie - Sets the character encoding that is used to interpret the query string
            #oe - Sets the character encoding that is used to encode the results
            #aq -?
            #num -1,10,100
            #client -- temp maintain to be firefox

            #may need to turn off personalize search pws = 0

            TODO:
            #need to add page num
            #with different agent --randomize this
            #take care of situation where the catchpa come out
            
        '''
        
        if type(google_search_keyword) == str:
            self.g_search_key = google_search_keyword
            self.multiple_search_enabled = 0
        elif type(google_search_keyword) == list:
            self.g_search_key_list = google_search_keyword
            self.g_search_key = ''
            self.multiple_search_enabled = 1
        else:
            print 'google_search_keyword not of type str or list'
            raise

        self.prefix_of_search_text = "https://www.google.com/search?q="
        self.search_results_num = 100 #only 1,10,100
        self.search_results_num_str = ''
        self.postfix_of_search_text = '&ie=utf-8&oe=utf-8&aq=t&rls=org.mozilla:en-US:official&client=firefox-a&channel=fflb'# non changable text
        self.output_url_str = ''
        self.data_format_switch = 1

        #storage of the various parameters
        self.setting_json_file = r'c:\data\temp\google_search'
        self.spider_name = 'Search'
        self.sp_allowed_domain = ['www.google.com']
        self.sp_search_url_list = []#place to put the search results
    

    def reformat_search_for_spaces(self):
        '''
            call immediately at the initialization stages
            get rid of the spaces and replace by the "+"
            None --> None
            steps:
            strip any lagging spaces if present
            replace the self.g_search_key
            

        '''
        self.g_search_key = self.g_search_key.rstrip().replace(' ', '+')

    def set_results_num_str(self, result_num):
        '''
            Function to set the number of results to the url str (temporary only for part of string)
            number of results can only be  1,10,100
            int results_num --> none
            Any other number entered will reset the results to 100
            have to set before the function format_search_url (TODO: defensive programming)
        '''
        if result_num not in [1,10,100]:
            print 'Results specified need to be in 1, 10 or 100. Values set to 100 by default'
            self.search_results_num = 100

        else:
            self.search_results_num = result_num

        self.search_results_num_str = '&num=%i'%self.search_results_num
        
    ## !!!
    def get_results_num_set(self):
        '''
          Return teh results number being set  

        '''

    ## !!!
    def set_page_query_num(self, page_num):
        '''
            Display the results of page x specify by the page_num
            int page_num --> none
            modified the
        '''

    def modify_search_key(self, purpose):
        '''
            This allow modification to the search key according to purpose
            str purpose --> none  (set to self.g_search_key)
            purpose: 'def' Get definition of word
        '''
        if purpose == 'def':
            self.g_search_key = 'define+' + self.g_search_key
        else:
            print 'purpose unknown: do nothing'
            pass ## no changes if the purpose is not defined

    def formed_search_url(self):
        '''
            Handle the different type of search: either one selected key phrases or multiple search items
            Depend on the input (self.multiple_search_enabled) will call the different function.
            Set to self.sp_search_url_list
        '''
        if not self.multiple_search_enabled:
            return self.formed_individual_search_url()
        else:
            return self.formed_multiple_search_url()


    def formed_individual_search_url(self):
        '''
            Function to get the formed url for search
            need the page num
            none --> str output_url_str
            set to tthe self.output_url_str and also return the string
            also set to self.sp_search_url_list
            
        '''
        self.reformat_search_for_spaces()

        if self.search_results_num_str =='':
            print 'seach output not being specified, Use default:100'
            self.set_results_num_str(100)

        self.output_url_str = self.prefix_of_search_text + self.g_search_key + self.search_results_num_str + self.postfix_of_search_text
    
        self.sp_search_url_list = [self.output_url_str]
        
        return  self.output_url_str

    ## !!!
    def formed_multiple_search_url(self):
        '''
            Function to create multiple search url by querying a list of phrases.
            For running consecutive search
            Use the formed_search_url to create individual search and store them in list
        
        '''
        temp_url_list = []
        ## get the individual url
        for n in self.g_search_key_list:
            ## set the individual key
            self.g_search_key = n
            temp_url_list.append(self.formed_individual_search_url())

        self.sp_search_url_list = temp_url_list
        return temp_url_list

    def prepare_data_for_json_store(self,additonal_parm_dict = {}):
        '''
            orgainized the data set for storing (trigger by self.data_format_switch)
            none, dict additonal_parm_dict --> dict 
            prepare a dict for read in to json --> a parameters to control the type of data input
            store and return as a dict
            additonal_parm_dict will add more user setting data to the data for storage
            
            inject a variable that differentiate between google search and other random website            
        '''
        if self.data_format_switch == 1:
            temp_data = {'Name':self.spider_name, 'Domain':self.sp_allowed_domain,
                        'SearchUrl':self.sp_search_url_list, 'type_of_parse':'google_search'}

        elif self.data_format_switch == 2:
            temp_data = {'Name':'random target website', 'Domain':[],
                        'SearchUrl':self.sp_search_url_list,'type_of_parse':'general'}
        else:
            raise
        
        temp_data.update(additonal_parm_dict)
        return temp_data        

    def print_list_of_data_format_for_json(self):
        '''
            Function to print out the various list of format prepared based on the data format switch (self.data_format_switch)
            None --> None
        '''
        print '1 -- google search \n 2 -- random website domain'

    def set_setting_to_json_file(self, data_dict):
        '''
            Function to set the various setting to json file
            dict data_dict --> none
            List of parameters to store (mainly for the spider to crawl
            name, allowed domains also in list (may leave blanks??), search url (list to be more than one???)

        '''
        with open(self.setting_json_file, "w") as outfile:
            json.dump(data_dict, outfile, indent=4)

    def retrieved_setting_fr_json_file(self, filename = ''):
        '''
            Function to retrieve the various setting from the json file specified by the self.setting_json_file
            None --> json object  setting_data
            set the various parameters

        '''
        if filename =='':
            filename = self.setting_json_file

        with open(filename, "r") as infile:
            setting_data = yaml.load(infile)

        return setting_data

if __name__ == '__main__':

    '''
        Running the google search

    '''
    # User options
    BYPASS_GOOGLE_SEARCH = 0    # if this is active, bypass searching
    NUM_RESULTS_TO_PROCESS = 30 # specify the number of results url to crawl

    print 'Start search'
    
    ## Parameters setting
    search_words = 'best area to stay in tokyo'
    search_words = ['best area to stay in tokyo','cheap place to stay in tokyo']
    GS_LINK_JSON_FILE = r'C:\data\temp\output' #must be same as the get_google_link_results.py

    # spider store location, depend on user input
    spider_file_path = r'C:\pythonuserfiles\google_search_module'
    spider_filename = 'Get_google_link_results.py'

    ## Google site link scrape
    if not BYPASS_GOOGLE_SEARCH:
        print 'Get the google search results links'
        hh = gsearch_url_form_class(search_words)
        hh.data_format_switch = 1
        hh.formed_search_url()
        ## Set the setting for json
        temp_data_for_store = hh.prepare_data_for_json_store()
        hh.set_setting_to_json_file(temp_data_for_store)
        new_project_cmd = 'scrapy settings -s DEPTH_LIMIT=1 & cd "%s" & scrapy runspider %s & pause' %(spider_file_path,spider_filename)
        os.system(new_project_cmd)
        
    ## Scape list of results link
    print 'Start scrape individual results'
    data  = hh.retrieved_setting_fr_json_file(GS_LINK_JSON_FILE)
    
    ##check if proper url --> must at least start with http
    url_links_fr_search = [n for n in data['output_url'] if n.startswith('http')]

    ## Switch to the second seach 
    hh.data_format_switch = 2

    ## Optional limit the results displayed
    hh.sp_search_url_list = url_links_fr_search[:NUM_RESULTS_TO_PROCESS]#keep the results to 10.Can be removed

    ## Set the setting for json
    temp_data_for_store = hh.prepare_data_for_json_store()
    hh.set_setting_to_json_file(temp_data_for_store)

    ## Run the crawler -- and remove the pause if do not wish to see contents of the command prompt
    new_project_cmd = 'scrapy settings -s DEPTH_LIMIT=1 & cd "%s" & scrapy runspider %s  & pause' %(spider_file_path,spider_filename)
    os.system(new_project_cmd)

    print 'Completed'    






