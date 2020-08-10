README
========

I will try to control my language and attitude. Diffusion problems give me a hot head. This represents my attempt to deal with `NPR's "effort" to improve their API`_. This represents my *first* efforts where I was able to *actually* get an `NPR Fresh Air`_ episode again, *sans* old working API.

I have made a separate Git branch that also lives on Github, ``dealing_with_npr_crap``. I order scratch notes by date.

10 AUGUST 2020
^^^^^^^^^^^^^^^

I stumbled upon the following method to get an `NPR Fresh Air`_ episode for a given day, say "May 4, 2020". Order this by follow-this-step-in-exact-order without corporate knowledge and necessary context. Sink-or-swim, ride-or-die.

1. ``May 4, 2020`` is a Monday, so get the ``datetime`` for the previous day, and get its timestamp.

   .. code-block:: python

      dt_start = datetime.datetime.strptime( 'May 3, 2020', '%B %d, %Y' )
      t_start = int( datetime.datetime.timestamp( dt_start ) )

   Here, ``t_start = 1588489200`` seconds.

2. The timestamp of the current day, "May 4, 2020", is,

   .. code-block:: python

      dt_end = datetime.datetime.strptime( 'May 4, 2020', '%B %d, %Y' )
      t_end = int( datetime.datetime.timestamp( dt_end ) )

   Here, ``t_end = 1588575600`` seconds.

3. Webscrap-y way, not API-correct way, to find the actual web page where an `NPR Fresh Air`_ episode lives. You have to go this URL without using the ``requests`` module which would make your life easier.

   .. code-block:: console

      https://www.npr.org/search?query=*&page=1&refinementList[shows]=FreshAir&range[lastModifiedDate][min]=<t_start>&range[lastModifiedDate][max]=<t_end>&sortType=byDateAsc

   In this case, since ``t_start = 1588489200`` and ``t_end = 1588575600``, the URL for this `NPR Fresh Air`_ episode request is,

   .. code-block:: console

      https://www.npr.org/search?query=*&page=1&refinementList[shows]=Fresh Air&range[lastModifiedDate][min]=1588489200&range[lastModifiedDate][max]=1588575600&sortType=byDateAsc

4. Now *of course* ``requests`` does not work, but the very slow Selenium Firefox webdriver functionality works. Make sure to install selenium with ``python3 -m pip install --user selenium``. Make sure to install geckodriver_ with ``sudo apt install firefox-geckodriver``. Here's how to get a headless Firefox Selenium driver running, go to tbhat website, and then create a ``BeautifulSoup`` XML tree of that page.

   .. code-block:: python

      from selenium import webdriver
      from selenium.webdriver.firefox.options import Options
      from bs4 import BeautifulSoup
      #
      ## create a headless Firefox
      options = Options( )
      options.headless = True
      driver = webdriver.Firefox( options = options )
      #
      ## now go to the NPR Fresh Air episode, and get the XML tree
      driver.get( 'https://www.npr.org/search?query=*&page=1&refinementList[shows]=Fresh Air&range[lastModifiedDate][min]=1588489200&range[lastModifiedDate][max]=1588575600&sortType=byDateAsc' )
      html = BeautifulSoup( driver.page_source, 'lxml' )

   If all goes well, only a *single* `NPR Fresh Air`_ episode is found, "Don't Worry, Even Fashion Guru Tim Gunn Is Living In His Comfy Clothes".

5. Extract the URL of that episode and use ``requests`` to get the web page for that URL

   .. code-block:: python

      import requests
      from urllib.parse import urljoin
      #
      ## get the elements that have the title and the URL to the episode
      episode_elems = html.find_all('h2', { 'class' : 'title' } )
      episode_urls = list(map(lambda elem: urljoin( 'https://www.npr.org', elem.find_all('a')[0]['href'] ), episode_elems ) )
      #
      ## now get the XML tree for that episode. It contains the episode description and the data
      for episode_url in episode_urls:
        response = requests.get( episode_url )
        assert( response.ok )
        html_ep = BeautifulSoup( response.content, 'lxml' )

6. Other information about each episode, define a method to get the title, order, and MP3 URL

   .. code-block:: python

      from urllib.parse import urlsplit
   
      def get_npr_freshair_story( episode_URL, candidate_date ):
        response = requests.get( episode_URL )
        assert( response.ok )
        html_ep = BeautifulSoup( response.content, 'lxml' )
        date_f = candidate_date.strftime( '%Y-%m-%d' )
	date_elems = list(html_ep.find_all('meta', { 'name' : 'date', 'content' : date_f } ) )
	if len( date_elems ) != 1: return None
        #
	## keep going, get the title    
        title_elems = list(html_ep.find_all('title'))
	if len( title_elems ) != 0: return None
	title = ' '.join(map(lambda tok: tok.strip(), title_elems[0].text.split(':')[:-1]))
	#
	## now get the MP3 URL
	mp3_elems = list(filter(lambda elem: 'href' in elem.attrs and 'mp3' in elem['href'], html_ep1.find_all('a')))
	if len( mp3_elems ) == 0: return None
	mp3_elem = mp3_elems[0]
	mp3_url_split = urlsplit( mp3_elem['href'] )
	mp3_url = urljoin( 'https://%s' % mp3_url_split.netloc, mp3_url_split.path )
	#
	## now get order
	order = int( os.path.basename( mp3_url ).split('.')[0].split('_')[-1] )
	#
	## return tuple of order, title, URL
	return order, title, mp3_url

   This should be sufficient in getting a ``tuple`` of ( ``order``, ``title``, ``mp3_url`` ) for a given story. All this information can be compiled in order to get the 
	
.. _`NPR Fresh Air`: https://freshair.npr.org
.. _`NPR's "effort" to improve their API`: https://www.reddit.com/r/NPR/comments/gfvzvg/can_we_get_story_info_and_download_stories_with/
.. _geckodriver: https://github.com/mozilla/geckodriver
