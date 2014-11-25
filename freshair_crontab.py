#!/usr/bin/env python

import freshair, datetime, time
import npr_utils

def freshair_crontab():
    """
    This python module downloads a Fresh Air episode on a particular weekday
    """

    # get current time
    current_date = datetime.date.fromtimestamp(time.time())
    if not npr_utils.is_weekday( current_date ):
        print "Error, today is not a weekday. Instead, today is %s." % \
            current_date.strftime('%A')
        return
    
    # now download the episode into the correct directory
    freshair.get_freshair('/mnt/media/freshair', current_date)

if __name__=='__main__':
    freshair_crontab()
    
