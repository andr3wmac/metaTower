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

import subprocess, threading, re

class ExecuteThread(threading.Thread):

    def __init__(self, cmd):
        threading.Thread.__init__(self)
        self.daemon = True
        self.cmd = cmd
        self.matchs = []
        self.include_err = True
        self.eofCallback = None
        self.lineCallback = None
        self.matchCallback = None
        self.running = True
        
    def run(self):
        p = subprocess.Popen([self.cmd],
            shell = True,             
            stderr=subprocess.STDOUT if self.include_err else None,
            stdout=subprocess.PIPE)
        stdout = p.stdout

        line = ""
        char = stdout.read(1)
        while ( char and self.running ):
            if ( char == '\r' or char == '\n' ):
                if ( self.lineCallback ): self.lineCallback(line)

                # if set, check for regex matche
                if ( self.matchCallback ):
                    for index in range(len(self.matches)):
                        match = self.matches[index]
                        results = re.findall(match, line)
                        if ( len(results) > 0 ): self.matchCallback(index, results)

                # clear line.
                line = ""
            else:
                line += char
            char = stdout.read(1)
        
        # we ran out of characters.
        if ( self.eofCallback ): self.eofCallback()

    def stop(self):
        self.running = False

