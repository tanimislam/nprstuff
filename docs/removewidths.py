#!/usr/bin/env python

import re, os, sys, pypandoc
from urlparse import urljoin

def remove_minipages_widths( latexfile, newfile ):
    lines = [ line.replace('\n', '') for line in open( latexfile, 'r' ) ]
    for idx in xrange(len(lines)):
        if '\\begin{minipage}' in lines[idx]:
            lines[idx] = re.sub('\[\!ht\].*', '', lines[idx])
    with open( newfile, 'w') as openfile:
        openfile.write('%s\n' % '\n'.join( lines ) )

def full_links_images( latexfile, newfile ):
    lines = [ line.replace('\n', '') for line in open( latexfile, 'r' ) ]
    for idx in xrange(len(lines)):
        if 'png' in lines[idx]:
            subURL = re.sub( '\}.*', '', re.sub('.*\{', '', lines[idx] ) ).strip( )
            newURL = urljoin( 'https://github.com/tanimislam/nprstuff/blob/master/docs/', subURL )
            lineAfter = re.sub('\{.*', '{%s}' % newURL, lines[idx] )
            lines[idx] = lineAfter
    with open( newfile, 'w') as openfile:
        openfile.write('%s\n' % '\n'.join( lines ) )

if __name__=='__main__':
    remove_minipages_widths( 'README.tex', 'foo.tex')
    full_links_images( 'foo.tex', 'foo.tex' )
    pypandoc.convert( 'foo.tex', 'rst', outputfile = 'README.rst' )
    pypandoc.convert( 'foo.tex', 'md', outputfile = 'README.md' )
    os.remove( 'foo.tex' )
