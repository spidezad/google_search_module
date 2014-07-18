"""
    GUI for the python google search.
    Allow more easy viewing of results.

    TODO:
    Set limit to the page scroller
    Input the multiple search options

    Learning:
        Trigger event\
        http://stackoverflow.com/questions/747781/wxpython-calling-an-event-manually
    


"""


import os
import sys
import wx
from Python_Google_Search import gsearch_url_form_class

import Extract_specified_txt_fr_files


class MyPanel(wx.Panel):
    def __init__(self, parent,*args, **kwds):
        self.parent = parent
        wx.Panel.__init__(self, parent, *args, **kwds)

        ## parameters
        self.page_scroller_result = dict()
        
        self.dummy_panel = wx.Panel(self, wx.ID_ANY)

        ## input search results.
        self.search_input_txtctrl = wx.TextCtrl(self, wx.ID_ANY, "")

        ## button for executing the search results
        self.search_btn = wx.Button(self, wx.ID_ANY, "search")
        self.search_btn.Bind(wx.EVT_BUTTON, self.run_search)

        ## incremental button for the page viewing
        self.page_scroller = wx.SpinCtrl(self, -1, "", (30, 50))
        self.page_scroller.SetRange(1,100)
        self.page_scroller.SetValue(1)
        self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.page_scroller)
        self.Bind(wx.EVT_TEXT, self.OnText, self.page_scroller)

        ## Display of search results
        self.results_txtctrl = wx.TextCtrl(self, wx.ID_ANY, "",
                                           style = wx.TE_MULTILINE| wx.TE_RICH2|wx.TE_WORDWRAP)

        ## for notes taking .
        self.notes_txtctrl = wx.TextCtrl(self, wx.ID_ANY, "",
                                           style = wx.TE_MULTILINE| wx.TE_RICH2|wx.TE_WORDWRAP)

        self.__do_layout()


    def __do_layout(self):

        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        mid_portion_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        
        sizer_2.Add(self.search_input_txtctrl, 5, wx.ALL | wx.EXPAND, 7)
        sizer_2.Add(self.search_btn, 0, wx.ALL | wx.EXPAND, 7)

        mid_portion_sizer.Add(self.page_scroller,1, wx.ALL | wx.EXPAND, 7)
        mid_portion_sizer.Add((-1,-1),4, wx.ALL | wx.EXPAND, 7)
        
        sizer_1.Add(sizer_2, 1, wx.ALL | wx.EXPAND, 3)
        sizer_1.Add(mid_portion_sizer, 1, wx.EXPAND, 0)
        sizer_1.Add(self.results_txtctrl, 10, wx.ALL | wx.EXPAND, 10)
        sizer_1.Add(self.notes_txtctrl, 5, wx.ALL | wx.EXPAND, 10)
        
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

    def OnSpin(self, evt):
        """Page Scroller function: on scroll. Scroll to correct page"""
        target_output = self.page_scroller_result[self.page_scroller.GetValue()]
        self.results_txtctrl.SetValue(target_output) 

    def OnText(self, evt):
        """Page Scroller function: on enter text. text to correct page"""
        target_output = self.page_scroller_result[self.page_scroller.GetValue()]
        self.results_txtctrl.SetValue(target_output)

    def trigger_scroller_event(self):
        """Manually trigger the event for the self.page_scroller to display the first set of result"""
        evt = wx.PyCommandEvent(wx.EVT_TEXT.typeId,self.page_scroller.GetId())
        self.GetEventHandler().ProcessEvent(evt) 

    def run_search(self, evt):
        """Run the google search """
        search_input = self.search_input_txtctrl.GetValue()
        self.execute_google_search(str(search_input))
        self.set_result_to_dict_for_page_scroller()
        self.clear_result_screen()
        self.trigger_scroller_event()

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

    def clear_result_screen(self):
        """Function to clear result screen (self.results_txtctrl"""
        self.results_txtctrl.SetValue('')

    def set_result_to_dict_for_page_scroller(self):
        """Store all result in dict to be used for page scroller"""
        key_symbol = '###'
        combined_result_list,self.page_scroller_result = Extract_specified_txt_fr_files.para_extract(r'c:\data\temp\htmlread_1.txt', key_symbol, overlapping = 0 )

    def join_list_of_str(self,list_of_str, joined_chars= ''):
        '''
            Function to combine a list of str to one long str
            list of str --> str

        '''
        return joined_chars.join([n for n in list_of_str])
    
    

class MyFrame(wx.Frame):
    def __init__(self, parent, ID, title):
               
        wx.Frame.__init__(self, parent, ID, title,pos=(150, 50), size=(550, 620))#size and position
        self.top_panel = MyPanel(self)

        ## Parameters
        self.save_notes_filename = ''

        ## Add in menu
        menuBar = wx.MenuBar()

        ## Menu keys
        menu1 = wx.Menu()
        menu1.Append(101, "Save", "")
        menu1.Append(102, "Save As", "")

        menuBar.Append(menu1, "File")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.menu_save_notes, id=101)
        self.Bind(wx.EVT_MENU, self.menu_save_as_notes, id=102)

    ## Menu functions --> need a function to retrieve the data
    def menu_save_notes(self, evt):
        """Save the notes options to the same file"""
        if self.save_notes_filename == '':
            ## do a save as if the file name not specified.
            self.menu_save_as_notes(8888)#dummy
        else:
            self.write_notes_data_to_file()

    def menu_save_as_notes(self, evt):
        """Open a dialog to save the file"""

        dlg = wx.FileDialog(
            self, message="Save file as ...", defaultDir=r'c:\data\temp', 
            defaultFile="",  style=wx.SAVE
            )


        dlg.SetFilterIndex(2)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.save_notes_filename = path

        dlg.Destroy()
        self.write_notes_data_to_file()

    def write_notes_data_to_file(self):
        """ Write all the notes to file"""
        with open(self.save_notes_filename, 'w') as f:
            f.write(self.top_panel.notes_txtctrl.GetValue())


        

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

 