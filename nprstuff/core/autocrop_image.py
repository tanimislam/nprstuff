import os, sys, webcolors, multiprocessing, numpy
import logging, subprocess, shlex, uuid
import matplotlib.image, matplotlib.colors
from PIL import Image, ImageChops
from PyPDF2 import PdfFileReader, PdfFileWriter
from itertools import chain
from distutils.spawn import find_executable

_all_possible_colornames = set(
    chain.from_iterable(
      map(lambda lst: list( lst.keys( ) ),
          [ webcolors.HTML4_NAMES_TO_HEX,
            webcolors.CSS2_NAMES_TO_HEX,
            webcolors.CSS21_NAMES_TO_HEX,
            webcolors.CSS3_NAMES_TO_HEX ] ) ) )

def autocrop_perproc( input_tuple ):
    """
    Designed to use Python's multiprocessing design to autocrop lossy images per processor.

    :param tuple input_tuple: a :py:class:`tuple` of ``inputfilename``, (input file name) ``outputfilename`` (output file name), ``color`` (background color), and ``fixEven`` (if ``True``, then resize the output image to have even-pixeled width and height).
    :returns: a :py:class:`tuple` of ``inputfilename`` and success status (``True`` for success, ``False`` otherwise).

    .. seealso:: :py:meth:`autocrop_image <nprstuff.core.autocrop_image.autocrop_image>`
    """
    inputfilename, outputfilename, color, fixEven = input_tuple
    val = autocrop_image(inputfilename, outputfilename = outputfilename, color = color, fixEven = fixEven)
    return inputfilename, val

def autocrop_image(inputfilename, outputfilename = None, color = 'white', newWidth = None,
                   doShow = False, trans = False, fixEven = False ):
    """
    performs an autocropping of lossy images, such as PNG_, JPEG_, or TIFF_,  with a defined background. The default background color is white. This then creates an automatically cropped image and stores into a new or the same file.
    
    :param str inputfilename: the input image file's name.
    :param str outputfilename: the output image file's name. If ``None``, then stores image into ``inputfilename``.
    :param str color: the background color over which to perform automatic cropping. Default is ``white``.
    :param int newWidth: the optional new width of the output image. If ``None``, then do not resize the image.
    :param bool doShow: if ``True``, then display the autocropped image using the computer's default image viewer (for example Preview_ on Mac OS X), otherwise output the autocropped into a file. Default is ``False``
    :param bool trans: if ``True``, then preserves the transparency of the input image. Default is ``False``.
    :param bool fixEven: If ``True``, then changes the width and height of the autocropped image so that both are divisible by 2. This functionality exists in order to create a movie (using FFMPEG_) from a sequence of image files; each image's width and height should all be the same, and *both divisible by 2*.
    :returns: a :py:class:`bool` of image processing status. ``True`` if able to perform the autocropping operation, ``False`` otherwise.
    :rtype: bool
    
    .. _PNG: https://en.wikipedia.org/wiki/Portable_Network_Graphics
    .. _JPEG: https://en.wikipedia.org/wiki/JPEG
    .. _TIFF: https://en.wikipedia.org/wiki/TIFF
    .. _Preview: https://en.wikipedia.org/wiki/Preview_(macOS)
    
    .. seealso:: :py:meth:`autocrop_image_perproc <nprstuff.core.autocrop_image.autocrop_image_perproc>`
    """
    im = Image.open(inputfilename)

    #
    ## if remove transparency, do the following
    ## follow instructions from https://twigstechtips.blogspot.com/2011/12/python-converting-transparent-areas-in.html
    if trans:
        im.convert( 'RGBA' )
        canvas = Image.new('RGBA', im.size, (255,255,255,255)) # Empty canvas colour (r,g,b,a)
        canvas.paste(im, mask = im) # Paste the image onto the canvas, using its alpha channel as mask
        im = canvas
    
    try:
        # get hex colors
        rgbcolor = numpy.array( matplotlib.colors.to_rgb( color ) )
    except Exception:
        if color not in _all_possible_colornames:
            raise ValueError("Error, color name = %s not in valid set of color names.")
        rgbcolor = numpy.array( webcolors.name_to_rgb(color), dtype=float ) / 255.0

    #
    ## code looks for FIRST color, in X and Y, that is NOT background color
    #
    ## step #1, get the numpy array representation, values are RGB(A), but only look at RGB
    ## RGB(A) values are from 0 to 1.0 inclusive
    img_data = matplotlib.image.imread( inputfilename )
    #
    ## now get the array of point coordinates (XVALS, YVALS) that are NOT background color
    try:
        #
        ## wtfism, imread transposes
        yvals, xvals = numpy.where(
            (img_data[:,:,0] != rgbcolor[0]) &
            (img_data[:,:,1] != rgbcolor[1]) &
            (img_data[:,:,2] != rgbcolor[2]) )
        left = xvals.min( )
        right = xvals.max( )
        upper = yvals.max( )
        lower = yvals.min( )
        bbox = ( left, lower, right, upper )
    except:
        bbox = ( 0, 0, im.size[0], im.size[1] )
    #
    ## crop image
    cropped = im.crop(bbox)
    if newWidth is not None:
        height = int( newWidth * 1.0 / cropped.size[0] * cropped.size[1] )
        cropped = cropped.resize(( newWidth, height ))

    if fixEven:
        sizeChanged = False
        newWidth, newHeight = cropped.size
        if newWidth % 2 != 0:
            newWidth += 1
            sizeChanged = True
        if newHeight % 2 != 0:
            newHeight += 1
            sizeChanged = True
        if sizeChanged: cropped = cropped.resize(( newWidth, newHeight ))
        
    if outputfilename is None:
        cropped.save(inputfilename)
    else:
        cropped.save(os.path.expanduser(outputfilename))
    if doShow:
        cropped.show( )
    return True
    #else:
    #    return False

#
## borrowed this code from https://gist.github.com/jpscaletti/7321281
## small changes:
## 1) all attributes and methods except for crop_pdf() are underscored
## 2) first search for "gs" executable. If there, then functionality can work
## 3) made a new method, crop_pdf_singlepage(), only for cropping SINGLE page (image) PDF files
"""
Pdfcrop
=======

Based on pdfcrop.pl_. Uses the BoundingBox [#]_

Dependencies:
  - PyPDF2_
  - ghostscript_


.. [#] http://commons.wikimedia.org/wiki/File:PDF_BOX_01.svg

.. _PyPDF2: https://github.com/mstamy2/PyPDF2/
.. _pdfcrop.pl: ftp://ftp.tex.ac.uk/tex-archive/support/pdfcrop/pdfcrop.pl

"""

_root_logger = logging.getLogger()
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
_root_logger.addHandler(_handler )
_devnull = open(os.devnull, 'w')

def _bbox(value):
    """
    >>> _bbox('%%BoundingBox: 217 208 566 357')
    [217, 208, 566, 357]
    """
    _, bbox = value.split(':')
    return list(map(int, bbox.split()))


def _hiresbb(value):
    """
    >>> _hiresbb('%%HiResBoundingBox: 98.765997 63.935998 694.025979 497.591774')
    [98.765997, 63.935998, 694.025979, 497.591774]
    """
    _, bbox = value.split(':')
    return list(map(float, bbox.split()))


def get_boundingbox(pdfpath, hiresbb = False):
    """
    Given a PDF_ file, returns its BoundingBox_. Requires working ghostscript_ (``gs`` executable) to calculate the bounding box.
    
    .. code-block:: python

       get_boundingbox('/path/to/mypdf.pdf')   # doctest: +SKIP
       [[23, 34, 300, 555], [0, 0, 300, 555]]
    
    :param str pdfpath: the name of the PDF_ file.
    :param bool hiresbb: if ``True``, returns the ``hiresBoundingbox``; otherwise returns ``Boundingbox``.
    :returns: a :py:class:`list` of BoundingBox_, one per PDF_ page.
    :rtype: list
    :raises IOError: if the ghostscript_ executable could noty be found.

    
    .. _ghostscript: https://www.ghostscript.com
    .. _BoundingBox: https://commons.wikimedia.org/wiki/File:PDF_BOX_01.svg
    """
    gs_exec = find_executable( 'gs' )
    if gs_exec is None:
        raise IOError("Error, cannot find ghostscript executable")
    command = [ gs_exec, ] + shlex.split('-dSAFER -sDEVICE=bbox -dNOPAUSE -dBATCH' )
    command.append( pdfpath )
    process = subprocess.Popen(command, stdout=_devnull, stderr=subprocess.PIPE)
    out, err = process.communicate( )  # gs sends output to stderr
    err = err.decode('utf-8')
    if hiresbb:
        return list(map(_hiresbb, filter(lambda line: line.startswith('%%HiResBoundingBox'), err.split('\n'))))
    return list(map(_bbox, filter(lambda line: line.startswith('%%BoundingBox'), err.split('\n'))))

def _make_pdf(i, fname, page):
    pdf_out = PdfFileWriter()
    outputfile = '{0}{1}'.format(i, fname)
    with open(outputfile, 'wb') as fout:
        pdf_out.addPage(page)
        pdf_out.write(fout)

def crop_pdf(inputfile, outputfile = None):
    """
    Given a possible multi-page PDF_ file that consists of :math:`N \ge 1` pages, creates :math:`N` separate single-page autocropped PDF_ files for each page in the input PDF_ file. Given a file with name ``inputfile``, the collection of output files are named ``outputfile<idx>``, where ``<idx>`` is the page number. This uses :py:class:`PdfFileReader <PyPDF2.PdfFileReader>` to read in, and :py:class:`PdfFileWriter <PyPDF2.PdfFilerWriter>` to write out, PDF_ files.

    The Python functionality is a port of the `pdfcrop.pl`_ PERL script.
    
    :param str inputfile: the name of the input PDF_ file.
    :param str outputfile: optional argument, the prefix of the output PDF_ files. If ``None``, then the prefix is the part of ``inputfile`` with the ``.pdf`` suffix removed.

    .. seealso:: :py:meth:`crop_pdf_singlepage <nprstuff.core.crop_pdf_singlepage>`

    .. _`pdfcrop.pl`: ftp://ftp.tex.ac.uk/tex-archive/support/pdfcrop/pdfcrop.pl
    """
    logger = logging.getLogger(__name__)
    bboxes = get_boundingbox(inputfile)
    if outputfile is None:
        outputfile = 'cropped.{0}{1}'.format(*os.path.splitext(inputfile))
    logger.info('Writing pdf output to %s', outputfile)
    with open(inputfile, 'rb') as fin:
        pdf_in = PdfFileReader(fin)
        for i, bbox in enumerate(bboxes):
            left, bottom, right, top = bbox
            page = pdf_in.getPage( i )
            logger.debug('Original mediabox: %s, %s', page.mediaBox.lowerLeft, page.mediaBox.upperRight)
            logger.debug('Original boundingbox: %s, %s', (left, bottom), (right, top))
            page.mediaBox.lowerLeft = (left, bottom)
            page.mediaBox.upperRight = (right, top)
            logger.debug('modified mediabox: %s, %s', page.mediaBox.lowerLeft, page.mediaBox.upperRight)
            _make_pdf(i, outputfile, page)

def crop_pdf_singlepage(inputfile, outputfile = None ):
    """
    Given a *single-paged* PDF_ file, creates an autocropped output PDF_ file. This uses :py:class:`PdfFileReader <PyPDF2.PdfFileReader>` to read in, and :py:class:`PdfFileWriter <PyPDF2.PdfFilerWriter>` to write out, PDF_ files.
    
    The Python functionality is a port of the `pdfcrop.pl`_ PERL script.
    
    :param str inputfile: the name of the input PDF_ file.
    :param str outputfile: optional argument, the name of the output PDF_ file. If ``None``, then the autocropped output PDF_ file replaces the input PDF_ file.

    .. _seealso:: :py:meth:`crop_pdf <nprstuff.core.crop_pdf_singlepage>`
    """
    logger = _root_logger
    bboxes = get_boundingbox(inputfile)
    assert( len( bboxes ) == 1 ) # single page PDF
    sameFile = False
    if outputfile is None:
        sameFile = True
        outputfile = '%s.pdf' % ''.join(map(lambda idx: str(uuid.uuid4()), range(2)))
    pdf_in = PdfFileReader( open( inputfile, 'rb' ) )
    left, bottom, right, top = bboxes[0]
    page = pdf_in.getPage( 0 )
    logger.debug('Original mediabox: %s, %s', page.mediaBox.lowerLeft, page.mediaBox.upperRight)
    logger.debug('Original boundingbox: %s, %s', (left, bottom), (right, top))
    page.mediaBox.lowerLeft = (left, bottom)
    page.mediaBox.upperRight = (right, top)
    logger.debug('modified mediabox: %s, %s', page.mediaBox.lowerLeft, page.mediaBox.upperRight)
    #
    ## write out to this new file
    pdf_out = PdfFileWriter( )
    pdf_out.addPage( page )
    pdf_out.write( open(outputfile, 'wb') )
    if sameFile: os.rename( outputfile, inputfile )
