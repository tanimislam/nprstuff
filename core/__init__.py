__author__ = 'Tanim Islam'
__email__ = 'tanim.islam@gmail.com'

import sys, os
from functools import reduce

resourceDir = os.path.join( reduce(lambda x,y: os.path.dirname( x ), range(2), os.path.abspath(__file__) ),
                            'resources' )
assert( os.path.isdir( resourceDir ) )

# code to handle Ctrl+C, convenience method for command line tools
def signal_handler( signal, frame ):
    print( "You pressed Ctrl+C. Exiting...")
    sys.exit( 0 )
