import lxml.html, requests, time, os
from multiprocessing import Pool, cpu_count
from argparse import ArgumentParser

def _get_surahs(outdir = os.getcwd( ) ):
    surahs = [ ]
    top_url = 'http://quranicradio.com'
    tree = lxml.html.fromstring( requests.get( 'http://quranicaudio.com/quran/109').content )
    for elem in tree.iter('tr'):
        sura_elems = list(elem.iter('td'))
        if len(sura_elems) != 4: continue
        if 'class' in elem.keys(): continue
        num_sura = int( sura_elems[0].text.strip() )
        name_sura = max( sura_elems[1].iter('a') ).text.strip()
        mp3_url = 'http://download.quranicaudio.com/quran/abdurrashid_sufi/%03d.mp3' % num_sura
        surahs.append( ( num_sura, name_sura, mp3_url, outdir ) )
    return surahs

def _download_per_tuple(input_tuple):
  time0 = time.perf_counter( )
  num, name, mp3_url, outdir = input_tuple
  filename = os.path.join(outdir, '%03d.%s.mp3' % ( num, name ) )
  with open(filename, 'wb') as openfile:
    openfile.write( requests.get( mp3_url ).content )
  print( 'Downloaded Sura %03d - %s, in %0.3f seconds.' % ( num, name, time.perf_counter() - time0 ) )

def _download_all_surahs(surahs):
  time0 = time.time()
  with Pool( processes = cpu_count( ) ) as pool:
    list( pool.map(_download_per_tuple, surahs) )
    print( 'Downloaded all suras in %0.3f seconds.' % ( time.time() - time0) )

def _main( ):
  parser = ArgumentParser( )
  parser.add_argument(
    '--outdir', dest='outdir', action='store', type = str,
    default = os.getcwd( ),
    help = 'Directory to put this data into. Default is %s.' % os.getcwd() )
  args = parser.parse_args( )
  surahs = _get_surahs( outdir = args.outdir )
  _download_all_surahs( surahs )


