google_search_module
====================

Retrieve google results using python

Progam obtained the results links from google main page and each links are run separately using Scrapy. In this way, users have more flexibility in obtaining various information from individual websites. At present, only the title and meta contents are scrapped from each website. The other advantage is that is remove further dependency from Google html tag changes.

Dependency of script are Scrapy and yaml (for unicode handling). Both can be downloaded using PIP.

Scripts is divided into 2 parts. The main script for running is from Python_Google_Search.py. The get_google_link_results.py is the scrapy spider for crawling either the google search page or individual websites. The switch depends on the json setting file created.

More information can be obtained from: http://wp.me/p4nnkg-1i
