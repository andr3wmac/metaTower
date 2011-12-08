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
version = "0.4.0"

import mtCore
import sys, os, time

# These exist only to have the librarys included when
# using py-installer.
if False:
    import nntplib, shutil, commands
    import serial.win32, Queue

def main():
    try:
        mtCore.start(version)

        while ( mtCore.running ):
            time.sleep(0.1)

        return mtCore.restart
    except KeyboardInterrupt:
        mtCore.stop()

if __name__ == '__main__':
    restart = main()
    if ( restart ):
        print "Restarting.."
        python = sys.executable
        os.execl(python, python, * sys.argv)
    else:
        print "Exiting.."
