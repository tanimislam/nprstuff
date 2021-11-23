import os, sys, numpy, requests, warnings
from argparse import ArgumentParser
from bs4 import BeautifulSoup

warnings.simplefilter("ignore")

"""
This is a front-end to https://developer.github.com/v3/markdown/, which describes how to create HTML from Markdown using Github's Markdown converter.
"""

def _md_2_html( markdown_file, html_file, verify = True ):
  assert( os.path.isfile( markdown_file ) )
  assert( any(map(lambda tok: os.path.basename( markdown_file ).endswith( '.%s' % tok ), ( 'md', 'rst' ) ) ) )
  assert( not os.path.isdir( html_file ) )
  assert( os.path.basename( html_file ).endswith( '.html' ) )
  headers = { 'Content-Type' : 'text/markdown' }
  response = requests.post(
    'https://api.github.com/markdown', headers = headers,
    json = { 'text' : open( markdown_file, 'r' ).read( ), 'mode' : 'markdown' },
    verify = verify )
  if response.status_code != 200:
    raise ValueError("Error, could not create HTML from candidate Markdown file %s." % (
      os.path.basename( markdown_file ) ) )
  #
  ##
  html = BeautifulSoup( response.content, 'lxml' )
  with open( html_file, 'w' ) as openfile:
    openfile.write( '%s\n' % html.prettify( ) )

def _main( ):
  parser = ArgumentParser( )
  parser.add_argument( '-m', '--markdown', type=str, dest='markdown_file', action='store', required = True,
                       help = "Name of the markdown file to convert using GitHub's Markdown API." )
  parser.add_argument( '-o', '--output', type=str, dest='html_file', action='store',
                       help = "Name of the HTML file to write out. Default would be <name>.html if <name>.md is the input Markdown file." )
  parser.add_argument( '--noverify', dest='do_verify', action='store_false', default=True,
                       help = 'If chosen, do not verify SSL connections to GitHub' )
  #
  args = parser.parse_args( )
  #
  if args.html_file is None:
    html_file = os.path.join( os.path.dirname( args.markdown_file ),
                              os.path.basename( args.markdown_file ).replace('.md', '.html' ) )
  else: html_file = args.html_file
  #
  _md_2_html( args.markdown_file, html_file, verify = args.do_verify )
                    
