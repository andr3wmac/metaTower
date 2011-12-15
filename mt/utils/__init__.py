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

import inspect, uuid, commands, socket, os, errno, shutil
import ExecuteThread, ProfileTicket

profile_enabled = False
def setProfiling(value):
    global profile_enabled
    profile_enabled = value

def profile(args = []):
    global profile_enabled
    return ProfileTicket.ProfileTicket(args, profile_enabled)

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
    while True:
        try:
            result.append(s.pop())
        except KeyError:
            break
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
        else:
            os.remove(path)
    except:
        pass

def copy(src, dst):
    shutil.copy(src, dst)

def move(src, dst):
    shutil.move(src, dst)

def execute(cmd, include_err = True):
    e = ExecuteThread.ExecuteThread(cmd)
    e.include_err = include_err
    return e.get_output()

def execute_async(cmd, matches = [], include_err = True, eofCallback = None, lineCallback = None, matchCallback = None):
    e = ExecuteThread.ExecuteThread(cmd)
    e.matches = matches
    e.include_err = include_err
    e.eofCallback = eofCallback
    e.lineCallback = lineCallback
    e.matchCallback = matchCallback
    e.start()
    return e
