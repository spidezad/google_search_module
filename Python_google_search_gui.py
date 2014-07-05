"""
    GUI for the python google search.
    Allow more easy viewing of results.


"""


import os
import sys
import wx
from Python_Google_Search import gsearch_url_form_class


class MyPanel(wx.Panel):
    def __init__(self, parent,*args, **kwds):
        self.parent = parent
        wx.Panel.__init__(self, parent, *args, **kwds)
        
        self.dummy_panel = wx.Panel(self, wx.ID_ANY)

        ## input search results.
        self.search_input_txtctrl = wx.TextCtrl(self, wx.ID_ANY, "")

        ## button for executing the search results
        self.search_btn = wx.Button(self, wx.ID_ANY, "search")
        self.search_btn.Bind(wx.EVT_BUTTON, self.run_search)
        
        ## Display of search results
        self.results_txtctrl = wx.TextCtrl(self, wx.ID_ANY, "",
                                           style = wx.TE_MULTILINE| wx.TE_RICH2|wx.TE_WORDWRAP)

        self.__do_layout()


    def __do_layout(self):

        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        
        sizer_1.Add(self.dummy_panel, 1, wx.EXPAND, 0)
        sizer_2.Add(self.search_input_txtctrl, 5, wx.ALL | wx.EXPAND, 7)
        sizer_2.Add(self.search_btn, 0, wx.ALL | wx.EXPAND, 7)
        sizer_1.Add(sizer_2, 1, wx.ALL | wx.EXPAND, 3)
        sizer_1.Add(self.results_txtctrl, 13, wx.ALL | wx.EXPAND, 10)
        
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

    def run_search(self, evt):
        """Run the google search """
        search_input = self.search_input_txtctrl.GetValue()
        self.execute_google_search(str(search_input))
        self.display_result_to_screen()

    def execute_google_search(self, search_input):
        """Run the full google search"""

        print search_input
        
        # User options
        NUM_SEARCH_RESULTS = 5     # number of search results returned
        BYPASS_GOOGLE_SEARCH = 0    # if this is active, bypass searching
        NUM_RESULTS_TO_PROCESS = 30 # specify the number of results url to crawl

        print 'Start search'
        
        ## Parameters setting
        search_words = search_input
        #search_words = ['best area to stay in tokyo','cheap place to stay in tokyo']
        GS_LINK_JSON_FILE = r'C:\data\temp\output' #must be same as the get_google_link_results.py

        # spider store location, depend on user input
        spider_file_path = r'C:\pythonuserfiles\google_search_module'
        spider_filename = 'Get_google_link_results.py'

        ## Google site link scrape
        if not BYPASS_GOOGLE_SEARCH:
            print 'Get the google search results links'
            hh = gsearch_url_form_class(search_words)
            hh.data_format_switch = 1
            hh.set_results_num_str(NUM_SEARCH_RESULTS)
            hh.formed_search_url()
            ## Set the setting for json
            temp_data_for_store = hh.prepare_data_for_json_store()
            hh.set_setting_to_json_file(temp_data_for_store)
            new_project_cmd = 'scrapy settings -s DEPTH_LIMIT=1 & cd "%s" & scrapy runspider %s' %(spider_file_path,spider_filename)
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
        new_project_cmd = 'scrapy settings -s DEPTH_LIMIT=1 & cd "%s" & scrapy runspider %s' %(spider_file_path,spider_filename)
        os.system(new_project_cmd)

        print 'Completed'


    def display_result_to_screen(self):
        """Read the data from the file and display in at the screen"""
        with open(r'c:\data\temp\htmlread_1.txt','r') as f:
            all_data = f.readlines()
        self.results_txtctrl.SetValue(self.join_list_of_str(all_data))

    def join_list_of_str(self,list_of_str, joined_chars= ''):
        '''
            Function to combine a list of str to one long str
            list of str --> str

        '''
        return joined_chars.join([n for n in list_of_str])
    
    

class MyFrame(wx.Frame):
    def __init__(self, parent, ID, title):
               
        wx.Frame.__init__(self, parent, ID, title,pos=(150, 150), size=(550, 520))#size and position
        self.top_panel = MyPanel(self)

class MyApp(wx.App):
    def __init__(self):
        wx.App.__init__(self,redirect =False)
        self.frame= MyFrame(None,wx.ID_ANY, "Google Search")
        self.SetTopWindow(self.frame)    
        self.frame.Show()
        
def run():
    try:
        app = MyApp()
        app.MainLoop()
    except Exception,e:
        print e
        del app#make sure to include this


if __name__ == '__main__':

    run()

 