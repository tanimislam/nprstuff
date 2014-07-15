#!/usr/bin/env python

__author__ = 'Tanim Islam'

"""
This python program tries to re-download those NPR Fresh Air programs
that are shorter than 30 minutes, and which have a modification time
more than 90 days before the current time
"""

import os, sys, glob, multiprocessing
import mutagen.mp4, time, datetime, freshair

"""
This checks to see whether to modify this file
"""
def find_NPR_files_to_modify_perproc(filename):
	atoms = mutagen.mp4.Atoms(open(filename, 'rb'))
	info = mutagen.mp4.MP4Info(atoms, open(filename, 'rb'))
	if info.length > 1800: return None
	#
	# check modification time
	mtime = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
	ltime = datetime.datetime.fromtimestamp(time.time())
	tdelta = ltime - mtime
	if tdelta.days < 90: return None
	#
	# matches conditions, return filename and date associated with this time
	strdate = '.'.join(os.path.basename(filename).split('.')[2:5])
	mydate = time.strptime(strdate, '%d.%m.%Y')
	return mydate
        
def find_NPR_dates_to_fix():
	filenames_to_process = filter(lambda filename: os.path.basename(filename).startswith('NPR.FreshAir'),
                                      glob.glob('/mnt/media/freshair/*.m4a'))
	pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
	return set(filter(None, pool.map(find_NPR_files_to_modify_perproc, filenames_to_process)))

def process_dates(npr_dates_to_fix, verbose = False):
	if verbose and len(npr_dates_to_fix) > 0:
		print 'GOT %d dates to fix' % len(npr_dates_to_fix)
	time0 = time.time()
	for idx, mydate in enumerate(npr_dates_to_fix):
		freshair.get_freshair('/mnt/media/freshair', mydate)
		if verbose:
			print 'PROCESSED %d / %d DATES IN %0.3f SECONDS' % ( idx+1,
                                                                             len(npr_dates_to_fix), time.time() - time0)
	if verbose and len(npr_dates_to_fix) > 0:
		print 'PROCESSED ALL DATES IN %0.3f SECONDS' % ( time.time() - time0)

def freshair_fix_crontab(verbose = False):
	npr_dates_to_fix = find_NPR_dates_to_fix()
	process_dates(npr_dates_to_fix, verbose=verbose)

if __name__=='__main__':
	freshair_fix_crontab(True)
