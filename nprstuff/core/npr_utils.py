import calendar, numpy, time, datetime, os
import multiprocessing, multiprocessing.pool
from itertools import chain
from shutil import which
import urllib.parse as urlparse
from urllib.parse import urlencode
from nprstuff import session, NPRStuffConfig, resourceDir

def get_firefox_driver( ):
    """
    :returns: a Firefox_ Selenium_ headless :py:class:`Webdriver <selenium.webdriver.remote.webdriver.WebDriver>`.
    
    .. seealso:: :py:meth:`get_chrome_driver <nprstuff.core.npr_utils.get_chrome_driver>`.

    .. _Firefox: https://www.mozilla.org/en-US/firefox/new
    .. _Selenium: https://www.selenium.dev/documentation/en
    """
    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options
    geckodriver = which( 'geckodriver' )
    if geckodriver is None:
        raise ValueError("Error, could not find geckodriver to launch Selenium Firefox headless browser." )
    options = Options( )
    options.headless = True
    driver = webdriver.Firefox( options = options )
    return driver

def get_chrome_driver( ):
    """
    :returns: a Chromium_ Selenium_ headless :py:class:`Webdriver <selenium.webdriver.remote.webdriver.WebDriver>`.
    
    .. seealso:: :py:meth:`get_firefox_driver <nprstuff.core.npr_utils.get_firefox_driver>`.

    .. _Chromium: https://www.chromium.org/Home
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    chromedriver = which( 'chromedriver' )
    if chromedriver is None:
        raise ValueError("Error, could not find chromedriver to launch Selenium Chromium headless browser.")
    options = Options( )
    options.headless = True
    driver = webdriver.Chrome( options = options )
    return driver

def find_necessary_executables( ):
    """
    :returns: this method searches first for the avconv_, then the FFmpeg_, executable for audiovisual conversion. If it finds either executable, returns a :py:class:`dict` that looks like ``{ 'avconv' : <EXEC_PATH> }``, where ``<EXEC_PATH>`` is the executable's path. If it does NOT find it, returns ``None``.

    .. _avconv: https://en.wikipedia.org/wiki/Libav
    """
    ffmpeg_exec = None
    for ffmpeg_exc in ('avconv', 'ffmpeg'):
        ffmpeg_exec = which(ffmpeg_exc)
        if ffmpeg_exec is not None: break
    if ffmpeg_exec is None: return None
    #
    return { 'avconv' : ffmpeg_exec }

def store_api_key( npr_API_key ):
    """
    Stores a candidate NPR API key into the SQLite3_ configuration database.

    :param str npr_API_key: candidate NPR API key.
    :returns: the string ``"SUCCESS"`` if could store the new NPR API KEY. Otherwise, the string ``'ERROR, COULD NOT STORE NPR_DATA api.'``.
    :rtype: str
    
    .. seealso:: :py:meth:`get_api_key <nprstuff.core.npr_utils.get_api_key>`.
    """
    val = session.query( NPRStuffConfig ).filter( NPRStuffConfig.service == 'NPR_DATA' ).first( )
    init_data = { }
    if val is not None:
        init_data = val.data
        session.delete( val )
        session.commit( )
    init_data[ 'apikey' ] = npr_API_key
    newval = NPRStuffConfig( service = 'NPR_DATA', data = init_data )
    session.add( newval )
    session.commit( )
    return 'SUCCESS'
  
def get_api_key( ):
    """
    :returns: the NPR API key, stored in` the SQLite3_ configuration database.
    :rtype: str

    .. seealso:: :py:meth:`store_api_key <nprstuff.core.npr_utils.store_api_key>`.
    """
    val = session.query( NPRStuffConfig ).filter( NPRStuffConfig.service == 'NPR_DATA' ).first( )
    if val is None: raise ValueError("Error, NPR_DATA configuration does not exist." )
    init_data = val.data
    if 'apikey' not in init_data:
        raise ValueError("Error, configuration files has not defined an apikey.")
    return init_data[ 'apikey' ]

def store_freshair_downloaddir( freshair_downloaddir ):
    """
    Stores the default location of the `NPR Fresh Air`_ episodes into the SQLite3_ configuration database.

    :param str freshair_downloaddir: the default directory to download `NPR Fresh Air`_ episodes.
    :returns: the string ``"SUCCESS"`` if could store the default directory to download `NPR Fresh Air`_ episodes. Otherwise, the string ``'ERROR, COULD NOT STORE NPR_DATA FRESHAIR DIRECTORY.'``.
    :rtype: str
    
    .. seealso:: :py:meth:`get_freshair_downloaddir <nprstuff.core.npr_utils.get_freshair_downloaddir>`.
    """
    assert( os.path.isdir( os.path.abspath( freshair_downloaddir ) ) )
    val = session.query( NPRStuffConfig ).filter( NPRStuffConfig.service == 'NPR_DATA' ).first( )
    init_data = { }
    if val is not None:
        init_data = val.data
        session.delete( val )
        session.commit( )
    init_data[ 'freshair_downloaddir' ] = os.path.abspath( freshair_downloaddir )
    newval =  NPRStuffConfig( service = 'NPR_DATA', data = init_data )
    session.add( newval )
    session.commit( )
    return "SUCCESS"

def get_freshair_downloaddir( ):
    """
    :returns: the `NPR Fresh Air`_ default download directory, stored in the SQLite3_ configuration database.
    :rtype: str
    
    .. seealso:: :py:meth:`store_freshair_downloaddir <nprstuff.core.npr_utils.store_freshair_downloaddir>`.
    """
    val = session.query( NPRStuffConfig ).filter( NPRStuffConfig.service == 'NPR_DATA' ).first( )
    if val is None: raise ValueError("Error, NPR_DATA configuration does not exist." )
    init_data = val.data
    if 'freshair_downloaddir' not in init_data:
        raise ValueError("Error, configuration file has not defined a default NPR Fresh Air download directory.")
    freshair_downloaddir = init_data[ 'freshair_downloaddir' ]
    assert( os.path.isdir( freshair_downloaddir ) )
    return freshair_downloaddir

def store_waitwait_downloaddir( waitwait_downloaddir ):
    """
    Stores the default location of the `NPR Fresh Air`_ episodes into the SQLite3_ configuration database.

    :param str waitwait_downloaddir: the default directory to download `NPR Wait Wait Air`_ episodes.
    :returns: the string ``"SUCCESS"`` if could store the default directory to download `NPR Wait Wairt`_ episodes. Otherwise, the string ``'ERROR, COULD NOT STORE NPR_DATA WAITWAIT DIRECTORY.'``.
    :rtype: str
    
    .. seealso:: :py:meth:`get_waitwait_downloaddir <nprstuff.core.npr_utils.get_waitwait_downloaddir>`.
    """
    assert( os.path.isdir( os.path.abspath( waitwait_downloaddir ) ) )
    val = session.query( NPRStuffConfig ).filter( NPRStuffConfig.service == 'NPR_DATA' ).first( )
    init_data = { }
    if val is not None:
        init_data = val.data
        session.delete( val )
        session.commit( )
    init_data[ 'waitwait_downloaddir' ] = os.path.abspath( waitwait_downloaddir )
    newval =  NPRStuffConfig( service = 'NPR_DATA', data = init_data )
    session.add( newval )
    session.commit( )
    return "SUCCESS"

def get_waitwait_downloaddir( ):
    """
    :returns: the `NPR Wait Wait`_ default download directory, stored in the SQLite3_ configuration database.
    :rtype: str
    
    .. seealso:: :py:meth:`store_waitwait_downloaddir <nprstuff.core.npr_utils.store_waitwait_downloaddir>`.
    """
    val = session.query( NPRStuffConfig ).filter( NPRStuffConfig.service == 'NPR_DATA' ).first( )
    if val is None: raise ValueError("Error, NPR_DATA configuration does not exist." )
    init_data = val.data
    if 'waitwait_downloaddir' not in init_data:
        raise ValueError("Error, configuration file has not defined a default NPR Wait Wait download directory.")
    waitwait_downloaddir = init_data[ 'waitwait_downloaddir' ]
    assert( os.path.isdir( waitwait_downloaddir ) )
    return waitwait_downloaddir
  
def get_decdate(date_s):
    """
    :param str date_s: a *decoded* date string, of the format "DD.MM.YYYY". This is a suffix attached to intermediate files that are created when downloading NPR shows.
    :returns: a :py:class:`datetime <datetime.datetime>` object associated with this date string.
    :rtype: :py:class:`datetime <datetime.datetime>`
    """
    return date_s.strftime('%d.%m.%Y')

def get_NPR_URL(date_s, program_id, NPR_API_key):
    """
    get the NPR API tag for a specific NPR program.
    
    :param str date_s: a date string formatted as "YYYY-MM-DD".
    :param int program_id: the NPR program's integer ID.
    :param str NPR_API_key: the NPR API key.
    :returns: a :py:class:`str` of the exploded URL for REST API calls to the NPR API server.
    :rtype: str
    
    .. note::

       no methods call this function any more, instead using the :py:mod:`requests` module's cleaner, higher-level functionality of REST API commands.
    """
    nprApiDate = date_s.strftime('%Y-%m-%d')
    result = urlparse.ParseResult(scheme = 'https', netloc = 'api.npr.org', path='/query', params='',
                                  query = urlencode({ 'id' : program_id,
                                                     'date' : nprApiDate,
                                                     'dateType' : 'story',
                                                     'output' : 'NPRML',
                                                     'apiKey' : NPR_API_key }), fragment = '')
    return result.geturl( )

def weekdays_of_month_of_year( year, month ):
    r"""
    :param int year: input year.
    :param int month: input month as an integer from 1 (January) through 12 (December).
    :returns: a sorted :py:class:`list` of days in a calendar month that are weekdays, each of which ranges from first (1) to last day of month. Each day is an integer :math:`\ge 1`.
    :rtype: list

    .. seealso:: :py:meth:`saturdays_of_month_of_year <nprstuff.core.npr_utils.saturdays_of_month_of_year>`.
    """
    days = sorted(
        filter(lambda day: day != 0,
            numpy.array( calendar.monthcalendar(year, month), dtype=int)[:,0:5].flatten() ) )
    return days

def saturdays_of_month_of_year( year, month ):
    r"""
    :param int year: input year.
    :param int month: input month as an integer from 1 (January) through 12 (December).
    :returns: a sorted :py:class:`list` of days in a calendar month that are Saturdays, each of which ranges from first (1) to last day of month. Each day is an integer :math:`\ge 1`.
    :rtype: list

    .. seealso:: :py:meth:`weekdays_of_month_of_year <nprstuff.core.npr_utils.weekdays_of_month_of_year>`.
    """
    days = sorted(
        filter(lambda day: day != 0,
               numpy.array( calendar.monthcalendar(year, month), dtype=int)[:,5].flatten() ) )
    return days

def get_time_from_datestring(datestring):
    """
    :param str datestring: a formatted date string, which must be of the form "January 1, 2014".
    :returns: a :py:class:`date <datetime.date>` object represented by that formatted date string.
    :rtype: :py:class:`date <datetime.date>`
    """
    return datetime.datetime.strptime(datestring, '%B %d, %Y').date( )

def get_datestring( date_act ):
    """
    :param datetime date_act: the candidate :py:class:`datetime <datetime.datetime>` to format.
    :returns: a :py:class:`str`, with the format like "January 1, 2014", of this :py:class:`datetime <datetime.datetime>`.
    :rtype: str

    .. seealso:: :py:meth:`get_time_from_datestring <nprstuff.core.npr_utils.get_time_from_datestring>`.
    """
    return date_act.strftime('%B %d, %Y')

def is_weekday(date_act):
    """
    :param date date_act: candidate date.
    :returns: whether the :py:class:`date <datetime.date>` is a weekday.
    :rtype: bool
    """
    return date_act.weekday() in list(range(5))
                                    
def is_saturday(date_act):
    """
    :param date date_act: candidate date.
    :returns: whether the :py:class:`date <datetime.date>` is a Saturday.
    :rtype: bool
    """
    return date_act.weekday() == 5

def is_sunday(dtime):
    """
    :param date date_act: candidate date.
    :returns: whether the :py:class:`date <datetime.date>` is a Sunday.
    :rtype: bool
    """
    return date_act.weekday() == 6

def get_order_number_weekday_in_year(date_act):
    """
    Returns the *1-indexed* order of the weekday associated with a given :py:class:`date <datetime.date>`. NOTE: this object MUST be a weekday.

    :param date date_act: the candidate weekday.

    :returns: a :py:class:`tuple` of *1-indexed* order of the weekday, and total number of weekdays, in the year in which this date exists.
    
    :rtype: tuple

    .. seealso:: 

         * :py:meth:`get_order_number_saturday_in_year <nprstuff.core.npr_utils.get_order_number_saturday_in_year>`.
         * :py:meth:`get_weekday_times_in_year <nprstuff.core.npr_utils.get_weekday_times_in_year>`.
         * :py:meth:`is_weekday <nprstuff.core.npr_utils.is_weekday>`.
    """
    assert( is_weekday(date_act ) )
    year_of_dtime = date_act.year
    all_wkdays_sorted = get_weekday_times_in_year( year_of_dtime )
    num = all_wkdays_sorted.index( date_act )
    return (num+1), len( all_wkdays_sorted )

def get_order_number_saturday_in_year( date_act ):
    """
    Returns the *1-indexed* order of the Saturday associated with a given :py:class:`date <datetime.date>`. NOTE: this object MUST be a Saturday.

    :param date date_act: the candidate Saturday.

    :returns: a :py:class:`tuple` of *1-indexed* order, and total number of Saturdays, in the year in which this Saturday exists.
    
    :rtype: tuple

    .. seealso:: 

         * :py:meth:`get_order_number_weekday_in_year <nprstuff.core.npr_utils.get_order_number_weekday_in_year>`.
         * :py:meth:`get_saturday_times_in_year <nprstuff.core.npr_utils.get_saturday_times_in_year>`.
         * :py:meth:`is_saturday <nprstuff.core.npr_utils.is_saturday>`.
    """
    assert( is_saturday(date_act ) )
    year_of_dtime = date_act.year
    all_saturdays_sorted = get_saturday_times_in_year( year_of_dtime )
    num = all_saturdays_sorted.index( date_act )
    return (num+1), len( all_saturdays_sorted )

def get_saturday_times_in_year(year, getAll = True):
    """
    Returns a sorted :py:class:`list` of Saturdays, as :py:class:`date <datetime.date>` objects for a given year, either *all* the Saturdays or all the Saturdays before now.

    :param int year: the year over which to find the weekdays.
    :param bool getAll: if ``True``, then return *all* the Saturdays. If ``False``, return those Saturdays before today.

    :returns: a sorted :py:class:`list` of Saturdays as a :py:class:`date <datetime.date>` objects.
    
    :rtype: list

    .. seealso:: :py:meth:`get_weekday_times_in_year <nprstuff.core.npr_utils.get_weekday_times_in_year>`.
    """
    nowd = datetime.datetime.now( ).date( )
    initsats = sorted(chain.from_iterable(
        map(lambda month: map(lambda day: datetime.date( year, month, day ), saturdays_of_month_of_year(year, month) ),
            range(1, 13 ) ) ) )
    if getAll: return initsats
    return list(filter(lambda day: dat < nowd, initsats ) )
    
def get_weekday_times_in_year(year, getAll = True):
    """
    Returns a sorted :py:class:`list` of weekdays, as :py:class:`date <datetime.date>` objects for a given year, either *all* the weekdays or all the weekdays before now.

    :param int year: the year over which to find the weekdays.
    :param bool getAll: if ``True``, then return *all* the weekdays. If ``False``, return those weekdays before today.

    :returns: a sorted :py:class:`list` of weekdays as a :py:class:`date <datetime.date>` objects.
    
    :rtype: list

    .. seealso:: :py:meth:`get_saturday_times_in_year <nprstuff.core.npr_utils.get_saturday_times_in_year>`.
    """
    inittimes = sorted(chain.from_iterable(
        map(lambda month: map(lambda day: datetime.date( year, month, day ),
                              weekdays_of_month_of_year( year, month ) ),
            range(1, 13 ) ) ) )
    if getAll: return inittimes
    #
    nowd = datetime.datetime.now( ).date( )
    return list( filter(lambda actd: actd < nowd, inittimes ) )

class MyPool(multiprocessing.pool.Pool):
    """
    A magic type of :py:class:`Pool <multiprocessing.pool.Pool>` whose processes can spawn other processes. This allows one to create a pool of workers that can spawn other processes (by default, :py:mod:`multiprocessing` does not allow this).
    
    I copied the code from `this website`_ and `a new website`_, without any real understanding EXCEPT that I am extending a :py:class:`Pool <multiprocessing.Pool>`.

    .. _`this website`: https://stackoverflow.com/a/8963618/3362358
    .. _`a new website`: https://stackoverflow.com/questions/52948447/error-group-argument-must-be-none-for-now-in-multiprocessing-pool 
    """
    def Process(self, *args, **kwds):
        proc = super(MyPool, self).Process(*args, **kwds)

        class NonDaemonProcess(proc.__class__):
            """Monkey-patch process to ensure it is never daemonized"""
            @property
            def daemon(self):
                return False

            @daemon.setter
            def daemon(self, val):
                pass
        #
        proc.__class__ = NonDaemonProcess
        return proc
