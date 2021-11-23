import glob, time, os, datetime, pyexiv2
from argparse import ArgumentParser
from dateutil.relativedelta import relativedelta
from multiprocessing import Pool, cpu_count

def _change_date_of_file(input_tuple):
  jpegfilename, minus, actdate = input_tuple
  current_year = time.localtime().tm_year
  metadata = pyexiv2.ImageMetadata(jpegfilename)
  metadata.read()
  yrs = 1
  if minus: yrs = -1
  for tagname in filter(lambda tn: tn in metadata,
                        ( 'Exif.Image.DateTime',
                          'Exif.Photo.DateTimeOriginal',
                          'Exif.Photo.DateTimeDigitized' ) ):
    tag = metadata[tagname]
    if actdate is None:
      year_pic = tag.value.year
      if current_year != year_pic:
        tag.value = tag.value + relativedelta(years = yrs)
      else:
        hour = tag.value.hour
        minute = tag.value.minute
        second = tag.value.second
        microsecond = tag.value.microsecond
        year = actdate.year
        month = actdate.month
        day = actdate.day
      tag.value = datetime.datetime(
        year, month, day, hour, minute, second, microsecond )
  metadata.write()
  stime = os.stat(jpegfilename)
  dt_plus1 = datetime.datetime.fromtimestamp( stime.st_mtime ) + \
    relativedelta(years = yrs)
  os.utime( jpegfilename, 
            ( stime.st_atime, time.mktime( dt_plus1.timetuple()) ) )
  
def _change_date_of_movie(input_tuple):
  movfilename, minus, actdate = input_tuple 
  stime = os.stat(movfilename)
  yrs = 1
  if minus: yrs = -1
  dt_plus1 = datetime.datetime.fromtimestamp( stime.st_mtime ) + \
    relativedelta(years = yrs)
  os.utime( movfilename, 
            ( stime.st_atime, time.mktime( dt_plus1.timetuple()) ) )

def _change_date_on_dir_movie(dirname, minus = False, actdate = None):
  time0 = time.time()
  if not os.path.isdir(dirname):
    raise ValueError("Error, %s is not a directory." % 
                     dirname )
  movfilenames = sorted(
    chain.from_iterable(map(lambda strng:
                            glob.glob(os.path.join(dirname, 'DSCN*.%s' % strng),
                                      ( 'mov', 'MOV' ) ) ) ) )
  with Pool( processes = cpu_count( ) ) as pool:
    movfilenames_tup = list(map(lambda movfile: ( movfile, minus, actdate ), movfilenames ) )
    list( pool.map(change_date_of_movie, movfilenames_tup) )
    print( 'Processed %d files in %s in %0.3f seconds.' % (
      len(movfilenames), dirname, time.time() - time0 ) )

def _change_date_on_dir(dirname, minus = False, actdate = None):
  time0 = time.time()
  if not os.path.isdir(dirname):
    raise ValueError("Error, %s is not a directory." % 
                     dirname )
  jpegfilenames = sorted(
    chain.from_iterable(map(lambda strng:
                            glob.glob(os.path.join(dirname, 'DSCN*.%s' % strng) ),
                            ( 'jpg', 'JPG', 'jpeg', 'JPEG' ) ) ) )
  with Pool( processes = cpu_count( ) ) as pool:
    jpegfilenames_tup = list(map(lambda jpegfilename: (jpegfilename, minus, actdate), 
                                 jpegfilenames ) )
    list( pool.map(_change_date_of_file, jpegfilenames_tup ) )
    print( 'Processed %d files in %s in %0.3f seconds.' % (
      len(jpegfilenames), dirname, time.time() - time0 ) )

def _main( ):
  parser = ArgumentParser( )
  parser.add_argument('--dirname', dest='dirname', action='store', type=str,
                      help = 'Name of the directory to look for jpeg files.',
                      required = True )
  parser.add_argument('--movs', dest='do_movs', action='store_true',
                      default = False,
                      help = 'If chosen, process MOV files instead.')
  parser.add_argument('--minus', dest="do_minus", action='store_true',
                      default = False,
                      help = 'If chosen, subtract a year from the files.') 
  args = parser.parse_args( )
  if args.dirname is None:
    raise ValueError("Error, must give a directory name.")
  if not args.do_movs:
    _change_date_on_dir( os.path.expanduser( args.dirname ),
                        minus = args.do_minus )
  else:
    _change_date_on_dir_movie(
      os.path.expanduser( args.dirname ),
      minus = args.do_minus )
