#!/usr/bin/env python

import os, glob, pyexiv2, time
import multiprocessing, datetime
from PIL import Image
from dateutil.relativedelta import relativedelta
from optparse import OptionParser

def is_jpg(filename):
    try:
        img = Image.open(filename)
        return img.format =='JPEG'
    except IOError:
        return False

def update_pic(jpegfilename):
    if not is_jpg(jpegfilename):
        return False
    
    metadata = pyexiv2.ImageMetadata(jpegfilename)
    metadata.read()
    #
    keys = filter(lambda key: 'DateTime' in key,
                  metadata.exif_keys)
    for key in keys:
        tag = metadata[key]
        dt = tag.value
        dtnew = dt + relativedelta(years=1)
        tag.value = dtnew
    metadata.write()
    return True

def update_mov(movfilename):
    sinfo = os.stat(movfilename)
    file_mtime = sinfo.st_mtime
    dtnew = datetime.datetime.fromtimestamp( file_mtime) + relativedelta(years=1)
    new_mtime = time.mktime( dtnew.timetuple() )
    os.utime( movfilename, ( new_mtime, new_mtime ) )

def process_directory_mov(dirname):
    if not os.path.isdir(dirname):
        raise ValueError("Error, %s is not a directory." % dirname )
    time0 = time.time()
    files = sorted( glob.glob( os.path.join(dirname, '*.MOV')))
    pool = multiprocessing.Pool(processes = multiprocessing.cpu_count())
    pool.map( update_mov, files )


def process_directory_pic(dirname):
    if not os.path.isdir(dirname):
        raise ValueError("Error, %s is not a directory." % dirname )
    time0 = time.time()
    files = sorted(
        filter(lambda fname: os.path.basename(fname).startswith('DSCN'),
               glob.glob( os.path.join(dirname, '*.JPG'))))
    pool = multiprocessing.Pool(processes = multiprocessing.cpu_count())
    vals = pool.map( update_pic, files )
    print 'processed files in %s in %0.3f seconds' % \
        ( dirname, time.time() - time0 )
    print '%d / %d files good.' % ( len(filter(lambda val: val is True, vals)),
                                    len(files) )

if __name__=='__main__':
    parser = OptionParser()
    parser.add_option( '--dir', dest='dirname', type=str, action='store',
                       help = 'Name of the directory into which to modify the file data. Default is %s' % os.getcwd(),
                       default = os.getcwd())
    opts, args = parser.parse_args()
    if not os.path.isdir( opts.dirname ):
        raise ValueError("Error, %s is not a directory." % opts.dirname )
    process_directory_pic( opts.dirname )
    process_directory_mov( opts.dirname )

