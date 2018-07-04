#!/usr/bin/env python3

import thisamericanlife, datetime, time, feedparser
import npr_utils, logging, glob, os, sys
from mutagen.id3 import ID3

_talurl = 'http://feed.thisamericanlife.org/talpodcast'

def _get_track( filename ):
    assert( os.path.basename( filename ).endswith( '.mp3' ) ) 
    mp3tags = ID3( filename ) 
    if 'TRCK' not in mp3tags: return None 
    return int( mp3tags['TRCK'].text[0] )

def _get_epno( entry ):
    if 'title' not in entry: return -1
    title = entry['title']
    epno = int( title.split(':')[0].strip( ) )
    return epno

def thisamericanlife_crontab( ):
    """
    This python module downloads a This American Life episode every weekend
    """
    
    # get all track numbers, and find what's left
    episodes_here = set(filter(None, map(
        _get_track, glob.glob('/mnt/media/thisamericanlife/PRI.ThisAmericanLife.*mp3' ) ) ) )
    #episodes_left = set( range( 1, max( episodes_here ) + 1 ) ) - episodes_here

    #
    ## from RSS feed, find latest episode number
    d = feedparser.parse( 'http://feed.thisamericanlife.org/talpodcast' )
    epno = _get_epno( max(d['entries'], key = lambda ent: _get_epno( ent ) ) )
    if epno not in episodes_here:
        time0 = time.time( )
        logging.debug('downloading This American Life epsiode #%03d' % epno )
        try:
            thisamericanlife.get_american_life( epno )
            logging.debug("finished downloading This American Life episode #%03d in %0.3f seconds" % (
                epno, time.time( ) - time0 ) )
        except:
            print( "Could not download This American Life episode #%03d" % epno )
    else:
        print( "Already have This American Life episode #%03d" % epno )

if __name__=='__main__':
    thisamericanlife_crontab( )

