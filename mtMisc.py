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

import inspect, uuid, commands, socket, os, errno, shutil

def uid():
    return str(uuid.uuid1()).replace("-", "")

def getSource(depth=2):
    try:
        frm = inspect.stack()[depth]
        mod = inspect.getmodule(frm[0])
        source = mod.__name__
        if ( source.endswith(".") ): source = source[:len(source)-1]
    except:
        source = ""
    return source

def getLocalIP():
    ip = socket.gethostbyname(socket.gethostname())
    if ( ip.startswith("127.") ):
        ifargs = commands.getoutput("ifconfig | grep 192.").split(" ")
        for arg in ifargs:
            if ( arg.startswith("addr:") ): ip = arg.split(":")[1]

        # Only way it seems to work when metaTower is running from init.d
        if ( not ip.startswith("192.") ):
            ifargs = commands.getoutput("/sbin/ifconfig | /bin/grep 192.").split(" ")
            for arg in ifargs:
                if ( arg.startswith("addr:") ): ip = arg.split(":")[1]
    return ip

def isLocalIP(IP):
    if ( IP[:7] == "192.168" ) or ( IP[:5] == "127.0" ) or ( IP[:5] == "10.0." ):
        return True
    return False

def removeDuplicates(arr):
    s = set(arr)
    result = []
    try:
        result.append(s.pop())
    except KeyError:
        pass
    return result

def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise

def rmdir(path):
    try:
        if ( os.path.isdir(path) ):
            shutil.rmtree(path, True)
            os.rmdir(path)
    except:
        pass
