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

import mt, sys, os, time, cProfile

def main():
    try:
        mt.start(version)

        while ( mt.running ):
            time.sleep(0.1)

        return mt.restart

    except KeyboardInterrupt:
        mt.stop()

if __name__ == '__main__':
    cProfile.run("restart = main()", "mtProfile")
    if ( restart ):
        print "Restarting.."
        python = sys.executable
        os.execl(python, python, * sys.argv)
    else:
        print "Exiting.."
