#!/usr/bin/env python

import waitwait, time

def waitwait_crontab():
    """
    This python module downloads a Wait Wait... episode on a particular Saturday
    """

    # get current time
    current_time = time.localtime()
    if current_time.tm_wday != 5:
        print "Error, today is not a Saturday. Instead, today is %s." % \
            time.strftime('%A', current_time)
        return
    
    # now download the episode into the correct directory
    waitwait.get_waitwait('/mnt/media/waitwait', current_time)

if __name__=='__main__':
    waitwait_crontab()
    
