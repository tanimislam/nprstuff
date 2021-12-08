import os, sys, numpy, base64
from io import BytesIO
from bs4 import BeautifulSoup
from PIL import Image
from argparse import ArgumentParser

def _create_image_base64( img_path ):
    assert( os.path.exists( img_path ) )
    with Image.open( img_path ) as img, BytesIO( ) as buffered:
        img.save( buffered, format = img.format )
        img_str = base64.b64encode( buffered.getvalue()).decode('utf8')
        return img_str

def _inline_images( input_html_file, output_html_file = None ):
    assert( os.path.isfile( input_html_file ) )
    assert( os.path.basename( input_html_file ).endswith('.html'))
    ofile = input_html_file
    if output_html_file is not None:
        assert( os.path.basename( output_html_file ).endswith( '.html' ) )
        ofile = output_html_file
    #
    ## first load in the input html file
    html = BeautifulSoup( open( input_html_file, 'r' ), 'lxml' )
    #
    ## now look for all the elems that have a src in them and exist on disk
    img_elems = list(
        filter(lambda elem: 'src' in elem.attrs and os.path.exists( elem['src'] ), html.find_all('img')))
    #
    ## turn them into base64 strings
    for elem in img_elems:
        elem['src'] = 'data:image/png;base64,%s' % _create_image_base64( elem['src'] )
    #
    ## now output into ofile
    with open( ofile, 'w' ) as openfile:
        openfile.write('%s\n' % html.prettify( ) )

def _main( ):
    parser = ArgumentParser( )
    parser.add_argument('-i', '--input', dest='input', type=str, action='store', required = True,
                        help = 'Name of input HTML file that (possibly) contains images to inline.' )
    parser.add_argument('-o', '--output',dest='output', type=str, action='store',
                        help = "Name of the output HTML file. Optional. If not set, then will rewrite input file." )
    args = parser.parse_args( )
    #
    ##
    ifile = os.path.expanduser( args.input )
    assert( os.path.isfile( ifile ) )
    assert( os.path.basename( ifile ).endswith('.html'))
    _inline_images( ifile, args.output )
