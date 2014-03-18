#!/usr/bin/env python

import freshair, time

def freshair_crontab():
    """
    This python module downloads a Fresh Air episode on a particular weekday
    """

    # get current time
    current_time = time.localtime()
    if current_time.tm_wday not in xrange(6):
        print "Error, today is not a weekday. Instead, today is %s." % \
            time.strftime('%w', current_time)
        return
    
    # now download the episode into the correct directory
    freshair.get_freshair('/mnt/media/freshair', current_time)

if __name__=='__main__':
    freshair_crontab()
    
