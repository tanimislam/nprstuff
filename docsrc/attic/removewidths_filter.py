#!/usr/bin/env python

from pandocfilters import toJSONFilter, walk, Str, Space, Link, Image
from pandocfilters import Para
import logging

def caps(key, value, format, meta):
    if key == 'Str':
        return Str(value.upper() )

# def deconcat(key, value, format, meta):
#     if isinstance( value, list):
#         if len(value) == 2:
#             url = Str( value[-1][0] )
#             name = Str( ' '.join([ 
#             return Link([' '.join([ walk( val, deconcat, format, meta ) for val in value ])], [ url ] )
#     if key == 'Str':
#         return Str( value )
#     elif key == 'Space':
#         return Space([ ])

def pchecko(key, value, format, meta):
    logging.debug('HUUU %s: %s' % (key, value ) )

def imStuff(key, value, format, meta):
    if key == 'Image':
        logging.debug('%s: %s, %d' % ( key, value[-1], len(value) ) )
        # return walk(value[-1], pchecko, format, meta )
        #[[ident, classes, kvs], contents] = value
        #logging.debug('CLASSES: %s' % classes )
        caption, location = value
        # now concatenate the content        
        logging.debug('%s: content = %s, %d' % ( key, caption, len(caption) ) )
        return Image([ Str("hello") ], [ location[0], location[1] ] )
                
if __name__=='__main__':
    logging.basicConfig( filename = 'removewidths_filter.log', level = logging.DEBUG )
    toJSONFilter( imStuff )
