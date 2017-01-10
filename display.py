#!/usr/bin/env python

from PIL import Image
import sys

if __name__=='__main__':
    if len( sys.argv ) < 2:
        print 'Error, syntax is display.py <imagefile>'
        sys.exit(0)
    try:
        img = Image.open( sys.argv[1] )
        img.show( )
    except:
        print 'Error, could not open %s' % sys.argv[1]
        sys.exit( 0 )
