#!/usr/bin/env python3

import os
from optparse import OptionParser
from core import autocrop_image

if __name__=='__main__':
    parser = OptionParser()
    parser.add_option('--input', dest='input', action='store', type=str,
                      help = 'Name of the input file.')
    parser.add_option('--output', dest='output', action='store', type=str,
                      help = 'Name of the output file. Optional.')
    parser.add_option('--color', dest='color', action='store', type=str,
                      help = 'Name of the color over which to autocrop. Default is white.',
                      default = 'white')
    parser.add_option('--newwidth', dest='newwidth', action='store', type=int,
                      help = 'New width of the image.' )
    parser.add_option('--show', dest='do_show', action='store_true', default = False,
                      help = 'If chosen, then show the final image after cropped.' )
    opts, args = parser.parse_args()
    if opts.input is None:
        raise ValueError("Error, input file path must be defined.")
    if not os.path.isfile(os.path.expanduser(opts.input)):
        raise ValueError("Error, candidate file = %s is not a file." % os.path.expanduser(opts.input))
    if not os.path.basename( opts.input ).endswith('.pdf'):
        autocrop_image.autocrop_image( os.path.expanduser(opts.input), outputfilename = opts.output, color = opts.color,
                                       newWidth = opts.newwidth, doShow = opts.do_show )
    else:
        if opts.output is not None: assert( os.path.basename( opts.output ).endswith('.pdf' ) )
        autocrop_image.crop_pdf_singlepage( os.path.expanduser( opts.input ), outputfile = opts.output )
