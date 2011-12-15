"""
 * metaTower v0.4.0
 * http://www.metatower.com
 *
 * Copyright 2011, Andrew W. MacIntyre
 * http://www.andrewmac.ca
 * Licensed under GPL v3.
 * See license.txt 
 *  or http://www.metatower.com/license.txt
"""
import mt, sys, os, time

VERSION = "0.4.0"
LOG_LEVEL = 10
PROFILING = False

try:
    mt.start(VERSION, LOG_LEVEL, PROFILING)

    while ( mt.running ):
        time.sleep(0.1)

except KeyboardInterrupt:
    mt.stop()
    print "Exiting.."
        
