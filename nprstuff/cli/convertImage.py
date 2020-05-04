import os, signal
from nprstuff import signal_handler
signal.signal( signal.SIGINT, signal_handler )
from nprstuff.core import convert_image
from argparse import ArgumentParser
    
def _main( ):
    parser = ArgumentParser( description = 'Uses CloudConvert to convert image or video files.' )
    #
    ## top level arguments
    parser.add_argument('-f', '--filename', dest='filename', type=str, action='store',
                        help = 'Name of the input image or video (MP4) file.', required = True )
    parser.add_argument('--noverify', dest='do_verify', action='store_false', default = True,
                        help = 'If chosen, do not verify the SSL connection.')
    #
    ## check whether to convert movie or video
    subparsers = parser.add_subparsers( help = 'Choose whether to convert a video or an image', dest = 'choose_option' )
    parser_image = subparsers.add_parser( 'image', help = 'If chosen, convert an SVG(Z), PDF, or PNG into PNG.' )
    parser_movie = subparsers.add_parser( 'movie', help = 'If chosen, convert an MP4 into an animated GIF.' )
    parser_square= subparsers.add_parser('square', help = 'If chosen, create a square MP4 file from an input MP4 file.' )
    #
    ## convert image
    parser_image.add_argument('--width', dest='width', type=int, action='store',
                              help = 'If defined, new width of the file. Optional')
    parser_image.add_argument('--pdf', dest='do_pdf', action='store_true', default = False,
                              help = 'If chosen, convert a PDF, instead of SVG(Z), file into PNG.')
    parser_image.add_argument('--png', dest='do_png', action='store_true', default = False,
                              help = 'If chosen, convert a PNG, instead of SVG(Z), file into a new PNG.')
    #
    ## square image
    parser_square.add_argument( '-o', '--output', dest='outputfilename', type=str, action='store',
                               required = True, help = 'Name of the output MP4 video that will be square.' )
    #
    ## parsing arguments
    args = parser.parse_args( )
    assert( args.filename is not None )
    #
    ## image
    if args.choose_option == 'image':
        assert( len( filter(lambda tok: tok is True, ( args.do_png, args.do_pdf ) ) ) <= 1 )
        if args.do_pdf:
            img = convert_image.get_png_image_frompdf( args.filename, newWidth = args.width, verify = args.do_verify )
            imgFile = os.path.basename( args.filename ).replace( '.pdf', '.png' )
        elif args.do_png:
            img = convert_image.get_png_image_frompng( args.filename, newWidth = args.width, verify = args.do_verify )
            imgFile = os.path.basename( args.filename ).replace( '.png', '_new.png' )
        else: # SVG or SVGZ
            img = convert_image.get_png_image( args.filename, newWidth = args.width, verify = args.do_verify )        
            imgFile = os.path.basename( args.filename ).replace('.svgz', '.png' ).replace('.svg', '.png')
        #
        ## now put into file
        dirName = os.path.dirname( os.path.abspath( args.filename ) )  
        img.save( os.path.join( dirName, imgFile ) )
        return
    #
    ## movie
    if args.choose_option == 'movie':
        img = convert_image.get_gif_video( args.filename )
        return
    #
    ## make square movie
    if args.choose_option == 'square':
        assert( os.path.basename( args.outputfilename ).endswith( '.mp4' ) )
        convert_image.make_square_mp4video(
            args.filename, args.outputfilename )
        return
