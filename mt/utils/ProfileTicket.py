"""
 * metaTower v0.4.0
 * http://www.metatower.com
 *
 * Copyright 2011, Andrew MacIntyre
 * http://www.andrewmac.ca
 * Licensed under GPL v3.
 * See license.txt 
 *  or http://www.metatower.com/license.txt
"""

import time, mt

class ProfileTicket:
    def __init__(self, args = [], enabled = True):
        if ( enabled ):
            self.start_time = time.time()
            self.end_time = 0
            self.start_args = args
            self.enabled = True
        else:
            self.enabled = False

    def end(self, args = []):
        if ( not self.enabled ): return
        src = mt.utils.getSource()
        self.end_time = time.time()
        args = self.start_args + args
        mt.log.profile("Profile of " + src + " ended in " + str(self.end_time-self.start_time) + " ARGS:" + str(args))
