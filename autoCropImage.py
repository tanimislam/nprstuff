#!/usr/bin/env python

import os, sys, webcolors, multiprocessing, functools, operator
from PIL import Image, ImageChops
from optparse import OptionParser

_all_possible_colornames = set( reduce( lambda y,x: y + x, [ webcolors.html4_names_to_hex.keys(),
                                                             webcolors.css2_names_to_hex.keys(),
                                                             webcolors.css21_names_to_hex.keys(),
                                                             webcolors.css3_names_to_hex.keys() ] ) )

def autocrop_perproc(input_tuple):
    inputfilename, outputfilename, color = input_tuple
    val = autocrop_image(inputfilename, outputfilename = outputfilename, color = color)
    return inputfilename, val
    

def autocrop_image(inputfilename, outputfilename = None, color = 'white'):
    im = Image.open(inputfilename)
    if color not in _all_possible_colornames:
        raise ValueError("Error, color name = %s not in valid set of color names.")
    rgbcolor = webcolors.name_to_rgb(color)
    bg = Image.new(im.mode, im.size, rgbcolor)
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        cropped = im.crop(bbox)
        if outputfilename is None:
            cropped.save(inputfilename)
        else:
            cropped.save(os.path.expanduser(outputfilename))
        return True
    else:
        return False

if __name__=='__main__':
    parser = OptionParser()
    parser.add_option('--input', dest='input', action='store', type=str,
                      help = 'Name of the input file.')
    parser.add_option('--output', dest='output', action='store', type=str,
                      help = 'Name of the output file. Optional.')
    parser.add_option('--color', dest='color', action='store', type=str,
                      help = 'Name of the color over which to autocrop. Default is white.',
                      default = 'white')
    opts, args = parser.parse_args()
    if opts.input is None:
        raise ValueError("Error, input file path must be defined.")
    if not os.path.isfile(os.path.expanduser(opts.input)):
        raise ValueError("Error, candidate file = %s is not a file." % os.path.expanduser(opts.input))
    autocrop_image( os.path.expanduser(opts.input), outputfilename = opts.output, color = opts.color)
