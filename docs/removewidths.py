#!/usr/bin/env python

import re, os, sys

def remove_minipages_widths( latexfile, newfile ):
    lines = [ line.replace('\n', '') for line in open( latexfile, 'r' ) ]
    print 'GOT HERE', len(lines)
    for idx in xrange(len(lines)):
        if '\\begin{minipage}' in lines[idx]:
            lines[idx] = re.sub('\[\!ht\].*', '', lines[idx])
    with open( newfile, 'w') as openfile:
        openfile.write('%s\n' % '\n'.join( lines ) )

if __name__=='__main__':
    remove_minipages_widths( 'README.tex', 'foo.tex')
