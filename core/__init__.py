__author__ = 'Tanim Islam'
__email__ = 'tanim.islam@gmail.com'

import sys, os
from functools import reduce

mainDir = reduce(lambda x,y: os.path.dirname( x ), range( 2 ),
                 os.path.abspath( __file__ ) )
resourceDir = os.path.join( mainDir, 'resources' )
assert(all(map(os.path.isdir, ( mainDir, resourceDir ) ) ) )
sys.path.append( mainDir )

# code to handle Ctrl+C, convenience method for command line tools
def signal_handler( signal, frame ):
  print( "You pressed Ctrl+C. Exiting...")
  sys.exit( 0 )
