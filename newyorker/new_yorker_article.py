#!/usr/bin/env python

import requests, lxml.html, textwrap, codecs, os
import datetime, pytz
from optparse import OptionParser

_send = u'\xa0\u2666'

def output_to_file(myurl, filename):
    if not filename.endswith('.txt'):
        raise ValueError("Error, %s does not end in .txt")
    
    # check if this is a valid url
    try:
        req = requests.get(myurl)
    except Exception:
        raise ValueError("Error, cannot get anything from %s." % myurl)


    tree = lxml.html.fromstring(req.text)
    paras = list( tree.iter('p') )
    last_idx = max( enumerate(paras), key = lambda tup:
                    _send in tup[1].text_content() )[0]
    if last_idx is None:
        raise ValueError("Error, could not find ending character in %s."
                         % myurl )
    para_texts = [ para.text_content() for para in paras[:last_idx+1] ]

    with codecs.open(filename, 'wb', 'utf-8') as outfile:
        for ptext in para_texts[:-1]:
            outfile.write('%s\n\n' % 
                          textwrap.fill(ptext))
        outfile.write('%s\n' % textwrap.fill(para_texts[-1]))

if __name__=='__main__':
    parser = OptionParser()
    parser.add_option('--url', dest='url', type=str, action='store',
                      help = ' '.join( [ 'Name of the New Yorker article URL that',
                                         'contains the article' ]) )
    parser.add_option('--filename', dest = 'filename', type=str, 
                      help = ' '.join( [ 'Name of the output file in which',
                                         'to store the article as a .txt file.',
                                         'Default is foo.txt.' ]),
                      default = 'foo.txt' )
    opts, args = parser.parse_args()
    if opts.url is None:
        raise ValueError("Error, must define the URL in which the New Yorker article is kept.")
    output_to_file( opts.url, opts.filename )
