"""
 * metaTower v0.4.5
 * http://www.metatower.com
 *
 * Copyright 2011, Andrew MacIntyre
 * http://www.andrewmac.ca
 * Licensed under GPL v3.
 * See license.txt 
 *  or http://www.metatower.com/license.txt
"""
import mt, sys, os, time

VERSION = "0.4.0"
LOG_LEVEL = 10
PROFILING = False

if mt.start(VERSION, LOG_LEVEL, PROFILING):
    try:
        raw_input()
    except KeyboardInterrupt:
        pass
    finally:
        mt.stop()
        
