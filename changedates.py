#!/usr/bin/env python

import pyexiv2, glob, time, os, datetime
from optparse import OptionParser
from dateutil.relativedelta import relativedelta
from multiprocessing import Pool, cpu_count

def change_date_of_file(jpegfilename):
    current_year = time.localtime().tm_year
    metadata = pyexiv2.ImageMetadata(jpegfilename)
    metadata.read()
    for tagname in filter(lambda tn: tn in metadata,
                          ( 'Exif.Image.Datetime',
                            'Exif.Photo.DateTimeOriginal',
                            'Exif.Photo.DateTimeDigitized' ) ):
        tag = metadata[tagname]
        year_pic = tag.value.year
        if current_year - year_pic == 1:
            tag.value = tag.value + relativedelta(years = 1)
    metadata.write()
    #
    # now change the modification time
    stime = os.stat(jpegfilename)
    dt_plus1 = datetime.datetime.fromtimestamp( stime.st_mtime ) + \
               relativedelta(years = 1)
    os.utime( jpegfilename, 
              ( stime.st_atime, time.mktime( dt_plus1.timetuple()) ) )

def change_date_of_movie(movfilename):
    current_year = time.localtime().tm_year
    stime = os.stat(movfilename)
    dt_plus1 = datetime.datetime.fromtimestamp( stime.st_mtime ) + \
               relativedelta(years = 1)
    os.utime( movfilename, 
              ( stime.st_atime, time.mktime( dt_plus1.timetuple()) ) )

def change_date_on_dir_movie(dirname):
    time0 = time.time()
    if not os.path.isdir(dirname):
        raise ValueError("Error, %s is not a directory." % 
                         dirname )
    movfilenames = sorted(
        reduce(lambda y, x: y + x,
               [ glob.glob(os.path.join(dirname, '*.%s' % strng)) for
                 strng in ( 'mov', 'MOV' ) ] ) )
    pool = Pool(processes = cpu_count())
    pool.map(change_date_of_movie, movfilenames)
    print 'Processed %d files in %s in %0.3f seconds.' % (
        len(movfilenames), dirname, time.time() - time0 )

def change_date_on_dir(dirname):
    time0 = time.time()
    if not os.path.isdir(dirname):
        raise ValueError("Error, %s is not a directory." % 
                         dirname )
    jpegfilenames = sorted(
        reduce(lambda y, x: y + x,
               [ glob.glob(os.path.join(dirname, '*.%s' % strng)) for
                 strng in ( 'jpg', 'JPG', 'jpeg', 'JPEG' ) ] ) )
    pool = Pool(processes = cpu_count())
    pool.map(change_date_of_file, jpegfilenames)
    print 'Processed %d files in %s in %0.3f seconds.' % (
        len(jpegfilenames), dirname, time.time() - time0 )

if __name__=='__main__':
    parser = OptionParser()
    parser.add_option('--dirname', dest='dirname', action='store', type=str,
                      help = 'Name of the directory to look for jpeg files.')
    parser.add_option('--movs', dest='do_movs', action='store_true',
                      default = False,
                      help = 'If chosen, process MOV files instead.')
    opts, args = parser.parse_args()
    if opts.dirname is None:
        raise ValueError("Error, must give a directory name.")
    if not opts.do_movs:
        change_date_on_dir( os.path.expanduser( opts.dirname ) )
    else:
        change_date_on_dir_movie( os.path.expanduser( opts.dirname) )
