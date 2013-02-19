"""
 * metaTower v0.4.5
 * http://www.metatower.com
 *
 * Copyright 2012, Andrew Mac
 * http://www.andrewmac.ca
 * Licensed under GPL v3.
 * See license.txt 
 *  or http://www.metatower.com/license.txt
"""

import subprocess, threading, re, os, mt

class ExecuteThread(threading.Thread):

    def __init__(self, cmd):
        threading.Thread.__init__(self)
        self.daemon = True

        # process cmd.
        if ( isinstance(cmd, list) ):
            new_list = []
            for item in cmd:
                args = item.split(" ")

                if ( len(args) == 1 ):
                    new_list.append(item)

                if ( len(args) > 1 ):
                    if ( os.name == "posix" ):
                        new_list.append("\\ ".join(args).replace("(", "\\(").replace(")", "\\)"))
                    if ( os.name == "nt" ):
                        new_list.append("\"" + item + "\"")

            self.cmd = " ".join(new_list)
        else:
            self.cmd = cmd

        # on posix we need it in an array, on nt we need just a string.
        if ( os.name == "posix" ): self.cmd = [self.cmd]

        # log the output command.
        mt.log.debug("Command to execute: " + str(self.cmd))

        # defaults.
        self.matchs = []
        self.include_err = True
        self.eofCallback = None
        self.lineCallback = None
        self.matchCallback = None
        self.running = True
        
    # used for a blocking read operation.
    def get_output(self):
        p = subprocess.Popen(self.cmd,
            shell = True,             
            stderr=subprocess.STDOUT if self.include_err else None,
            stdout=subprocess.PIPE)
        stdout = p.stdout
        output = stdout.read()
        mt.log.debug("stdout:\n" + output)
        return output

    # used for non-blocking read operation.
    def run(self):
        p = subprocess.Popen(self.cmd,
            shell = True,             
            stderr=subprocess.STDOUT if self.include_err else None,
            stdout=subprocess.PIPE)
        stdout = p.stdout

        line = ""
        char = stdout.read(1)
        while ( char and self.running ):
            if ( char == '\r' or char == '\n' ):
                if ( self.lineCallback ): 
                    self.lineCallback(line)

                # if set, check for regex matche
                if ( self.matchCallback ):
                    for index in range(len(self.matches)):
                        match = self.matches[index]
                        results = re.findall(match, line)
                        if ( len(results) > 0 ): self.matchCallback(index, results)

                # clear line.
                mt.log.debug("stdout: " + line)
                line = ""
            else:
                line += char
            char = stdout.read(1)
        
        # we ran out of characters.
        if ( self.eofCallback ): self.eofCallback()

    def stop(self):
        self.running = False

