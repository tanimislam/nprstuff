import os, sys, titlecase
from argparse import ArgumentParser

def _main( ):
    parser = ArgumentParser( )
    parser.add_argument(
        '-t',
        '--title', dest='title', type=str, action='store', default='',
        help = 'This is title title. Default is blank.')
    args = parser.parse_args( )
    if len(opts.title.strip()) == 0:
        print( '' )
    else:
        print( titlecase.titlecase( args.title.strip( ) ) )
