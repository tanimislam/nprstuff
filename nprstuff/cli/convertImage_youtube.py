import os, signal, logging
from nprstuff import signal_handler
signal.signal( signal.SIGINT, signal_handler )
from nprstuff.core import convert_image_youtube
from argparse import ArgumentParser
    
def _main( ):
    logger = logging.getLogger( )
    parser = ArgumentParser( description = 'Creates an animated GIF from a YouTube clip!' )
    #
    ## top level arguments
    parser.add_argument('--noverify', dest='do_verify', action='store_false', default = True,
                        help = 'If chosen, do not verify the SSL connection.')
    parser.add_argument('--info', dest='do_info', action = 'store_true',  default = False,
                        help = 'If chosen, then print out INFO level logging.' )
    #
    ## animated gif from youtube video
    parser.add_argument(
        '-u', '--url', dest='parser_url', type=str, action='store', metavar = 'url',
        help = 'YouTube URL of the input video.', required = True )
    parser.add_argument(
        '-o', '--output', dest='parser_output', type=str, action='store', metavar = 'output',
        help = 'Name of the output animated GIF file that will be created.', required = True )
    parser.add_argument(
        '-q', '--quality', dest='parser_quality', type=str, action='store', metavar = 'quality', default = 'highest',
        choices = ( 'highest', 'high', 'medium', 'low' ),
        help = 'The quality of the YouTube clip to download. Only video portion is downloaded. May be one of highest, high, medium, low. Default is highest.' )
    parser.add_argument(
        '-d', '--duration', dest='parser_duration', type=float, action='store', metavar = 'duration',
        help = 'Optional argument. If chosen, the duration (in seconds, from beginning) of the video to be converted into an animated GIF.' )
    parser.add_argument(
        '-s', '--scale', dest='parser_scale', type=float, action='store', metavar = 'scale', default = 1.0,
        help = 'Optional scaling of the input video. Default is 1.0.' )
    #
    ## parsing arguments
    args = parser.parse_args( )
    if args.do_info: logger.setLevel( logging.INFO )
    #
    ## animated gif from youtube video
    assert( os.path.basename( args.parser_output ).endswith( '.gif' ) )
    convert_image_youtube.youtube2gif(
        args.parser_url, args.parser_output,
        quality = args.parser_quality,
        duration = args.parser_duration,
        scale = args.parser_scale,
        verify = args.do_verify )
