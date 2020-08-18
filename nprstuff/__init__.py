__author__ = 'Tanim Islam'
__email__ = 'tanim.islam@gmail.com'

import sys, os, logging

_mainDir = os.path.dirname( os.path.abspath( __file__ ) )
resourceDir = os.path.join( _mainDir, 'resources' )
assert( os.path.isdir( resourceDir ) )

logging_dict = {
    "NONE" : 100,
    "INFO" : logging.INFO,
    "DEBUG": logging.DEBUG,
    "ERROR": logging.ERROR }

def _get_nprstuff_logger( ):
    logging.basicConfig(format = '%(levelname)s %(module)s.%(funcName)s (%(lineno)d): %(message)s' )
    return logging.getLogger( )
    # h = logging.StreamHandler( sys.stdout )
    #formatter = logging.Formatter(
    # #    '%{levelno}s %{module}s.%{filename}s.%{funcName}s: %{message}s' )
    # formatter = logging.Formatter(
    #     '%(asctime)s - %(message)s', style='{' )
    # h.setFormatter( formatter )
    # logger.addHandler( h )
    # return logger

# code to handle Ctrl+C, convenience method for command line tools
def signal_handler( signal, frame ):
    print( "You pressed Ctrl+C. Exiting...")
    sys.exit( 0 )

nprstuff_logger = _get_nprstuff_logger( )
# nprstuff_logger = logging.getLogger()
