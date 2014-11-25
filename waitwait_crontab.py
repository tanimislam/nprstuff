#!/usr/bin/env python

import waitwait, time, datetime
import npr_utils

def waitwait_crontab():
    """
    This python module downloads a Wait Wait... episode on a particular Saturday
    """

    # get current time
    current_date = datetime.date.fromtimestamp( time.time())
    if not npr_utils.is_saturday( current_date ):
        print "Error, today is not a Saturday. Instead, today is %s." % \
            current_date.strftime('%A')
        return
    
    # now download the episode into the correct directory
    waitwait.get_waitwait('/mnt/media/waitwait', current_date)

if __name__=='__main__':
    waitwait_crontab()
    
