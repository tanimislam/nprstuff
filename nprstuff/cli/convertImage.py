import os, signal, logging
from nprstuff import signal_handler
signal.signal( signal.SIGINT, signal_handler )
from nprstuff.core import convert_image
from argparse import ArgumentParser
    
def _main( ):
    logger = logging.getLogger( )
    parser = ArgumentParser( description = 'Uses CloudConvert to convert image or video files.' )
    #
    ## top level arguments
    parser.add_argument('--noverify', dest='do_verify', action='store_false', default = True,
                        help = 'If chosen, do not verify the SSL connection.')
    parser.add_argument('--info', dest='do_info', action = 'store_true',  default = False,
                        help = 'If chosen, then print out INFO level logging.' )
    #
    ## check whether to convert movie or video
    subparsers = parser.add_subparsers( help = 'Choose whether to convert a video or an image', dest = 'choose_option' )
    parser_image  = subparsers.add_parser( 'image',   help = 'If chosen, convert an SVG(Z), PDF, or PNG into PNG.' )
    parser_movie  = subparsers.add_parser( 'movie',   help = 'If chosen, convert an MP4 into an animated GIF.' )
    parser_youtube= subparsers.add_parser( 'youtube', help = 'If chosen, convert a YOUTUBE video with URL into an animated GIF.' )
    parser_square = subparsers.add_parser( 'square',  help = 'If chosen, create a square MP4 file from an input MP4 file.' )
    #
    ## convert image
    parser_image.add_argument(
        '-f', '--filename', dest='parser_image_filename', type=str, action='store', metavar = 'filename',
        help = 'Name of the input image file.', required = True )
    parser_image.add_argument('--width', dest='width', type=int, action='store',
                              help = 'If defined, new width of the file. Optional')
    parser_image.add_argument(
        '-F', '--format', dest='input_format', type=str, action='store',
        choices = ( 'svg', 'pdf', 'png' ), help = 'Format of input file. Must be one of SVG/SVGZ, PDF, or PNG.' )
    #
    ## square video
    parser_square.add_argument(
        '-f', '--filename', dest='parser_square_filename', type=str, action='store', metavar = 'filename',
        help = 'Name of the input video (MP4) file.', required = True )
    parser_square.add_argument( '-o', '--output', dest='outputfilename', type=str, action='store',
                               required = True, help = 'Name of the output MP4 video that will be square.' )
    #
    ## animated gif
    parser_movie.add_argument(
        '-f', '--filename', dest='parser_movie_filename', type=str, action='store', metavar = 'filename',
        help = 'Name of the input video (MP4) file.', required = True )
    #
    ## animated gif from youtube video
    parser_youtube.add_argument(
        '-u', '--url', dest='parser_youtube_url', type=str, action='store', metavar = 'url',
        help = 'YouTube URL of the input video.', required = True )
    parser_youtube.add_argument(
        '-o', '--output', dest='parser_youtube_output', type=str, action='store', metavar = 'output',
        help = 'Name of the output animated GIF file that will be created.', required = True )
    parser_youtube.add_argument(
        '-q', '--quality', dest='parser_youtube_quality', type=str, action='store', metavar = 'quality', default = 'highest',
        choices = ( 'highest', 'high', 'medium', 'low' ),
        help = 'The quality of the YouTube clip to download. Only video portion is downloaded. May be one of highest, high, medium, low. Default is highest.' )
    parser_youtube.add_argument(
        '-d', '--duration', dest='parser_youtube_duration', type=float, action='store', metavar = 'duration',
        help = 'Optional argument. If chosen, the duration (in seconds, from beginning) of the video to be converted into an animated GIF.' )
    parser_youtube.add_argument(
        '-s', '--scale', dest='parser_youtube_scale', type=float, action='store', metavar = 'scale', default = 1.0,
        help = 'Optional scaling of the input video. Default is 1.0.' )
    #
    ## parsing arguments
    args = parser.parse_args( )
    if args.do_info: logger.setLevel( logging.INFO )
    #
    ## image
    if args.choose_option == 'image':
        print( 'ERROR, CloudConvert sort of pooped the bed. This conversion functionality no longer works. Exiting...' )
        return
        # filename = args.parser_image_filename
        # if args.input_format == 'svg': # SVG or SVGZ
        #     img = convert_image.svg2png( filename, newWidth = args.width, verify = args.do_verify )        
        #     imgFile = os.path.basename( args.filename ).replace('.svgz', '.png' ).replace('.svg', '.png')
        # if args.input_format == 'pdf':
        #     img = convert_image.pdf2png( filename, newWidth = args.width, verify = args.do_verify )
        #     imgFile = os.path.basename( args.filename ).replace( '.pdf', '.png' )
        # if args.input_format == 'png':
        #     img = convert_image.png2png( filename, newWidth = args.width, verify = args.do_verify )
        #     imgFile = os.path.basename( filename ).replace( '.png', '_new.png' )
        # #
        # ## now put into file
        # dirName = os.path.dirname( os.path.abspath( filename ) )  
        # img.save( os.path.join( dirName, imgFile ) )
        # return
    #
    ## movie
    if args.choose_option == 'movie':
        img = convert_image.mp4togif( args.parser_movie_filename )
        return
    #
    ## make square movie
    if args.choose_option == 'square':
        assert( os.path.basename( args.outputfilename ).endswith( '.mp4' ) )
        convert_image.make_square_mp4video(
            args.parser_square_filename, args.outputfilename )
        return
    #
    ## animated gif from youtube video
    if args.choose_option == 'youtube':
        assert( os.path.basename( args.parser_youtube_output ).endswith( '.gif' ) )
        convert_image.youtube2gif(
            args.parser_youtube_url, args.parser_youtube_output,
            quality = args.parser_youtube_quality,
            duration = args.parser_youtube_duration,
            scale = args.parser_youtube_scale )

