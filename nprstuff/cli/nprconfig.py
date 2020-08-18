import os, sys, signal, logging
from nprstuff import signal_handler
signal.signal( signal.SIGINT, signal_handler )
import datetime, time, multiprocessing, glob, mutagen.mp4, tabulate
from nprstuff import logging_dict, nprstuff_logger as logger
from nprstuff.core import freshair, freshair_by_year, npr_utils
from argparse import ArgumentParser

def _show_npr_config( ):
    npr_api = "NONE"
    freshair_downloaddir = "NONE"
    waitwait_downloaddir = "NONE"
    try:
        npr_api = npr_utils.get_api_key( )
        freshair_downloaddir = npr_utils.get_freshair_downloaddir( )
        waitwait_downloaddir = npr_utils.get_waitwait_downloaddir( )
    except Exception as e:
        logging.info( str( e ) )
        pass

    data_toshow = [
        ( 'NPR API KEY', npr_api ),
        ( 'NPR Fresh Air download', freshair_downloaddir ),
        ( 'NPR Wait Wait download', waitwait_downloaddir ) ]
    print( 'NPR CONFIGURATION' )
    print( '%s\n' % tabulate.tabulate( data_toshow ) )
    
def main( ):
    """
    This either gets (and shows) or sets the following configuration settings.
    
    * the NPR API key.
    * The default download directory for `NPR Fresh Air`_ episodes.
    * The default download directory for `NPR Wait Wait`_ episodes.
    """
    parser = ArgumentParser( )
    parser.add_argument('--level', dest='level', action='store', type=str, default = 'NONE',
                        choices = sorted( logging_dict ),
                        help = 'choose the debug level for. Default is NONE.' % sorted( logging_dict ) )
    subparsers = parser.add_subparsers(
        help = ' '.join([
            'Choose one of these options:',
            '(show) shows the NPR core functionality settings.',
            '(set) sets the default download directory for NPR Fresh Air and NPR Wait Wait episodes.' ] ),
        dest = 'choose_option' )
    #
    ## just show the configuration options
    parser_showconfig = subparsers.add_parser( 'show', help = 'Just show the NPR core functionality settings.' )
    #
    ## set the default NPR Fresh Air and NPR Wait Wait download directories
    parser_defaultconfig = subparsers.add_parser( 'set', help = 'Set the default download directories for NPR Fresh Air and NPR Wait Wait episodes.' )
    parser_defaultconfig.add_argument( '--freshair', dest='defaultconfig_freshair', metavar='FRESHAIR', type=str,
                                      action = 'store', help = 'Sets the default download directory for NPR Fresh Air episodes.' )
    parser_defaultconfig.add_argument( '--waitwait', dest='defaultconfig_waitwait', metavar='WAITWAIT', type=str,
                                      action = 'store', help = 'Sets the default download directory for NPR Wait Wait episodes.' )
    parser_defaultconfig.add_argument( '--api', dest='defaultconfig_api', metavar='API', type=str,
                                      action = 'store', help = 'Sets the NPR API key.' )
    #
    ##
    args = parser.parse_args( )
    logger.setLevel( logging_dict[ args.level ] )
    #
    ## just show the NPR configuration
    if args.choose_option == 'show':
        _show_npr_config( )
        return
    elif args.choose_option == 'set':
        if args.defaultconfig_freshair is not None:
            npr_utils.store_freshair_downloaddir( args.defaultconfig_freshair )
        if args.defaultconfig_waitwait is not None:
            npr_utils.store_waitwait_downloaddir( args.defaultconfig_waitwait )
        if args.defaultconfig_api is not None:
            npr_utils.store_api_key( args.defaultconfig_api )
        _show_npr_config( )
        return
