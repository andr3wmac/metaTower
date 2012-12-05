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

import inspect, uuid, commands, socket, os, errno, shutil, hashlib, platform, ctypes, re
import ExecuteThread, ProfileTicket

profile_enabled = False
def setProfiling(value):
    global profile_enabled
    profile_enabled = value

def profile(args = []):
    global profile_enabled
    return ProfileTicket.ProfileTicket(args, profile_enabled)

def uid():
    #return guid.generate()
    return str(uuid.uuid4()).replace("-", "")

def md5(string):
    return hashlib.md5(string).hexdigest()

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
    ip = "127.0.0.1"

    # easiest way possible.
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except:
        pass

    if ( ip.startswith("127.") ):
        try:
            ifargs = commands.getoutput("ifconfig | grep 192.").split(" ")
            for arg in ifargs:
                if ( arg.startswith("addr:") ): ip = arg.split(":")[1]
        except:
            pass

        # Only way it seems to work when metaTower is running from init.d
        try:
            if ( not ip.startswith("192.") ):
                ifargs = commands.getoutput("/sbin/ifconfig | /bin/grep 192.").split(" ")
                for arg in ifargs:
                    if ( arg.startswith("addr:") ): ip = arg.split(":")[1]
        except:
            pass

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

def convert_bytes(bytes):
    bytes = float(bytes)
    if bytes >= 1099511627776:
        terabytes = bytes / 1099511627776
        size = '%.2fT' % terabytes
    elif bytes >= 1073741824:
        gigabytes = bytes / 1073741824
        size = '%.2fG' % gigabytes
    elif bytes >= 1048576:
        megabytes = bytes / 1048576
        size = '%.2fM' % megabytes
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        size = '%.2fK' % kilobytes
    else:
        size = '%.2fb' % bytes
    return size

def get_hdds():
    folder = "."
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
        return [["C", free_bytes.value]]
    else:
        hdds = []
        lines = commands.getoutput("/bin/df -BG").split("\n")
        for line in lines:
            if ( not line.startswith("/dev/") ): continue            

            line_args = []
            arg = ""
            for letter in line:
                if ( letter == " " ): 
                    if ( arg != "" ): line_args.append(arg)
                    arg = ""                    
                    continue
                else:
                    arg += letter

            hdd = {}
            if ( len(line_args) == 5 ):
                hdd["name"] = line_args[0]
                hdd["used"] = int(re.search('\d+', line_args[2]).group())
                hdd["available"] = int(re.search('\d+', line_args[3]).group())
                hdd["percent-used"] = line_args[4]
                hdd["total"] = hdd["available"] + hdd["used"]
                hdds.append(hdd)                 
              
        return hdds

        #if ( arg.startswith("addr:") ): ip = arg.split(":")[1]
        #s = os.statvfs(folder)
        #return s.f_bsize * s.f_bavail
    return []

def getCPUUsage():
    cpu_usage = -1.0
    if platform.system() == 'Windows':
        cpu_usage = -1 # placeholder
    else:
        lines = commands.getoutput("/usr/bin/top -b -n1").split("\n")
        for line in lines:
            # Cpu(s):  0.4%us,  0.1%sy,  0.0%ni, 99.4%id,  0.0%wa,  0.0%hi,  0.0%si,  0.0%st
            if ( line.startswith("%Cpu(s):") ):
                regex = '([0-9]+\\.[0-9]*)|([0-9]*\\.[0-9]+)|([0-9]+)'
                cpu_usage = float(re.search(regex, line).group())
    return cpu_usage

def getRAMInfo():
    ram_info = {"total": -1, "free": -1, "used:": -1}
    if platform.system() == 'Windows':
        cpu_usage = -1 # placeholder
    else:
        lines = commands.getoutput("/usr/bin/free -m").split("\n")
        for line in lines:
            # -/+ buffers/cache:        324       1683
            if ( line.startswith("-/+ buffers/cache:") ):
                info = re.findall("([0-9]+\\.[0-9]*)|([0-9]*\\.[0-9]+)|([0-9]+)", line)
                # output = [('', '', '324'), ('', '', '1683')]
                ram_info["used"] = int(info[0][2])
                ram_info["free"] = int(info[1][2])
                ram_info["total"] = ram_info["used"] + ram_info["free"]
    return ram_info
