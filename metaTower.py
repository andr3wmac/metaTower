"""
 * metaTower v0.3.2
 * http://www.metatower.com
 *
 * Copyright 2011, Andrew W. MacIntyre
 * http://www.andrewmac.ca
 * Licensed under GPL v3.
 * See license.txt 
 *  or http://www.metatower.com/license.txt
"""

import mtHTTPServer, mtAuth, mtCore
import sys, os

# These exist only to have the librarys included when
# using py-installer.
if False:
    import nntplib, libtorrent, shutil, commands
    import serial.win32, Queue

if __name__ == '__main__':
    print "metaTower v0.3.1"
    mtCore.start()
    mtAuth.start()
    mtHTTPServer.start()
    try:
        cmd = ""
        while ( cmd != "stop" ):
            sys.stdout.write("> ")
            cmd = raw_input()
            try:
                cmd_args = cmd.split(" ")
                if ( cmd_args[0] == "packages" ): mtCore.packages.listPackages()
                elif ( cmd_args[0] == "load" ): mtCore.packages.load(cmd_args[1], "packages")
                elif ( cmd_args[0] == "reload" ): mtCore.packages.reload(cmd_args[1])
                elif ( cmd_args[0] == "unload" ): mtCore.packages.unload(cmd_args[1])
                elif ( cmd_args[0] == "restart" ): mtCore.restart()
                elif ( cmd_args[0] == "stop" ): continue
                else: 
                    print "Commands:"
                    print "  packages - lists packages."
                    print "  load <name>"
                    print "  reload <name> - reloads a package."
                    print "  unload <name> - unloads a package."
                    print "  stop - shut down metaTower."
            except Exception as e:
                print "Error: " + str(e.args)
    finally:
        print "Shutting down.."
        if ( mtCore.running ): mtCore.stop()
        if ( mtCore.restart ):
                mtexe = sys.executable
                os.execl(mtexe, mtexe, * sys.argv)
