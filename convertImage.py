#!/usr/bin/env python3

import os
import core.convert_image
from argparse import ArgumentParser
    
if __name__=='__main__':
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
    #
    ## convert image
    parser.add_argument('--width', dest='width', type=int, action='store',
                        help = 'If defined, new width of the file. Optional')
    parser_image.add_argument('--pdf', dest='do_pdf', action='store_true', default = False,
                              help = 'If chosen, convert a PDF, instead of SVG(Z), file into PNG.')
    parser_image.add_argument('--png', dest='do_png', action='store_true', default = False,
                              help = 'If chosen, convert a PNG, instead of SVG(Z), file into a new PNG.')
    #
    ## parsing arguments
    args = parser.parse_args( )
    assert( args.filename is not None )
    #
    ## image
    if args.choose_option == 'image':
      assert( len( filter(lambda tok: tok is True, ( args.do_png, args.do_pdf ) ) ) <= 1 )
      if args.do_pdf:
        img = core.convert_image.get_png_image_frompdf( args.filename, newWidth = args.width, verify = args.do_verify )
        imgFile = os.path.basename( args.filename ).replace( '.pdf', '.png' )
      elif args.do_png:
        img = core.convert_image.get_png_image_frompng( args.filename, newWidth = args.width, verify = args.do_verify )
        imgFile = os.path.basename( args.filename ).replace( '.png', '_new.png' )
      else: # SVG or SVGZ
        img = core.convert_image.get_png_image( args.filename, newWidth = args.width, verify = args.do_verify )        
        imgFile = os.path.basename( args.filename ).replace('.svgz', '.png' ).replace('.svg', '.png')
    #
    ## movie
    if args.choose_option == 'movie':
      img = core.convert_image.get_gif_video( args.filename, verify = args.do_verify )
      imgFile = os.path.basename( args.filename ).replace( '.mp4', '.gif' )
    #
    ## now put into file
    dirName = os.path.dirname( os.path.abspath( args.filename ) )  
    img.save( os.path.join( dirName, imgFile ) )
