import os, signal, logging
from nprstuff import signal_handler
signal.signal( signal.SIGINT, signal_handler )
from nprstuff.core import convert_image
from argparse import ArgumentParser
    
def _main( ):
    logger = logging.getLogger( )
    parser = ArgumentParser( description = 'Now does five different things, where only "image" operates on image files!' )
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
    parser_aspected = subparsers.add_parser( 'aspected',  help = 'If chosen, create an aspected MP4 file from an input MP4 file.' )
    parser_fromimages = subparsers.add_parser( 'fromimages', help = 'If chosen, then convert a sequence of PNG/JPEG/TIF images into an MP4 file.' )
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
    parser_aspected.add_argument(
        '-f', '--filename', dest='parser_aspected_filename', type=str, action='store', metavar = 'filename',
        help = 'Name of the input video (MP4) file.', required = True )
    parser_aspected.add_argument( '-o', '--output', dest='outputfilename', type=str, action='store',
                               required = True, help = 'Name of the output MP4 video that will be square.' )
    parser_aspected.add_argument( '-a', '--aspect', dest='aspect', type=str, action='store', default = 'square',
                               choices = [ 'square', '916', '169' ],
                               help = 'The aspect ratio to choose for the final video. Can be one of three: "square" is 1:1, "916" is 9/16 (width 9 units, height 16 units), and "169" is 16/9 (width 16 units, height 9 units). Default is "square".')
    parser_aspected.add_argument( '-b', '--black', dest='do_black', action='store_true', default = False,
                               help = 'If chosen, then pad the sides OR the top and bottom with BLACK instead of WHITE. Default is to do WHITE.' )
    #
    ## animated gif
    parser_movie.add_argument(
        '-f', '--filename', dest='parser_movie_filename', type=str, action='store', metavar = 'filename',
        help = 'Name of the input video (MP4) file.', required = True )
    parser_movie.add_argument(
        '-s', '--scale', dest='parser_movie_scale', type=float, action='store', metavar='scale', default = 1.0,
        help = 'Multiply the width and height of the input MP4 file into the output GIF. Default is 1.0 (GIF file has same dimensions as input MP4 file). Must be greater than 0.')
    parser_movie.add_argument(
        '-d', '--dirname', dest='parser_movie_dirname', type=str, action='store',
        help = 'Optional argument. If defined, the directory into which to store the file.' )
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
    ## create an MP4 file from a sequence of images
    parser_fromimages.add_argument( '-d', '--dirname', dest='parser_fromimages_dirname', type=str, action='store', metavar='dirname', default = os.getcwd( ),
                                   help = 'The name of the directory to look for a sequence of PNG/JPEG/TIF images. Default is %s.' % os.getcwd( ) )
    parser_fromimages.add_argument( '-p', '--prefix', dest='parser_fromimages_prefix', type=str, action='store', metavar='prefix', required=True,
                                   help = 'The prefix of PNG/JPEG/TIF files through which to go.' )
    parser_fromimages.add_argument( '-s', '--imagesuffix', dest='parser_fromimages_suffix', type=str, action='store', metavar='suffix', default = 'png',
                                   help = 'The suffix of the image files. Default is png.' )
    parser_fromimages.add_argument( '-f', '--fps', dest='parser_fromimages_fps', type=int, action='store', metavar='fps', default = 5,
                                   help = 'The number of frames per second in the MP4 file. Default is 5.' )
    parser_fromimages.add_argument( '--autocrop', dest='parser_fromimages_do_autocrop', action='store_true', default = False,
                                   help = 'If chosen, then perform an autocrop, and then (where necessary) resize each image so that their widths and heights are multiples of 2.')
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
        assert( os.path.isfile( args.parser_movie_filename ) )
        dirname = os.path.dirname( os.path.dirname( args.parser_movie_filename ) )
        basname = os.path.basename( os.path.basename( args.parser_movie_filename ) )
        if args.parser_movie_dirname is not None:
            assert( os.path.isdir( args.parser_movie_dirname ) )
            dirname = args.parser_movie_dirname
        gif_file = os.path.join( dirname, basname.replace( '.mp4', '.gif' ) )
        assert( args.parser_movie_scale > 0 )
        img = convert_image.mp4togif(
            args.parser_movie_filename,
            gif_file = gif_file,
            scale = args.parser_movie_scale )
        return
    #
    ## make square movie
    if args.choose_option == 'aspected':
        assert( os.path.basename( args.outputfilename ).endswith( '.mp4' ) )
        background = 'white'
        if args.do_black: background = 'black'
        convert_image.make_aspected_mp4video(
            args.parser_aspected_filename, args.outputfilename,
            aspect = args.aspect, background = background )
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
        return
    #
    ## create an MP4 file from a collection of images
    if args.choose_option == 'fromimages':
        assert( os.path.isdir( args.parser_fromimages_dirname ) )
        images2mp4dict = convert_image.create_images2mp4dict(
            args.parser_fromimages_prefix,
            image_suffix = args.parser_fromimages_suffix,
            dirname = args.parser_fromimages_dirname,
            fps = args.parser_fromimages_fps,
            autocrop = args.parser_fromimages_do_autocrop )
        if images2mp4dict['status'] != 'SUCCESS':
            print( images2mp4dict['status'] )
            return
        #
        ## now perform the operation to autocrop those images
        convert_image.mp4fromimages( images2mp4dict )

