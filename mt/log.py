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

import logging, threads, time, os, utils, multiprocessing

class LogItem:
    def __init__(self, source, level, data, pid):
        self.source = source
        self.level = level
        self.data = data
        self.pid = pid

class LogThread(threads.Thread):
    def __init__(self, log_dir, main_pid):
        threads.Thread.__init__(self)
        self.daemon = True
        self.main_pid = main_pid
        self.queue = multiprocessing.Queue()
        self.log_dir = log_dir

    def run(self):
        file_handles = {}
        try:
            while self.running:
                try:
                    item = self.queue.get_nowait()

                    # only put PID in filename is different from main pid.
                    f_name = item.source + ".log"
                    if ( item.pid != self.main_pid ):
                        f_name = item.source + "." + str(item.pid) + ".log"

                    if ( not file_handles.has_key(f_name) ):
                        file_handles[f_name] = open(os.path.join(self.log_dir, f_name), "w")

                    file_handles[f_name].write(item.level + ": " + item.data + "\n")
                    file_handles[f_name].flush()
                except:
                    self.sleep(1)

        finally:
            for f in file_handles: 
                file_handles[f].close()

    def addItem(self, source, level, text, pid):
        i = LogItem(source, level, text, pid)
        self.queue.put_nowait(i)

# DEBUG       10
# INFO        20
# WARNING     30
# ERROR       40
# CRITICAL    50
# FATAL       50
log_level = 0
log_dir = "logs"
log_pid = 0
main_pid = 0
log_thread = None
names = {};

def addItem(name, level, text, level_num):
    global log_thread, log_pid, log_dir, main_pid

    if ( level_num > 10 ):
        color = "\033[92m"
        if ( level_num > 20 ): color = "\033[93m"
        if ( level_num > 30 ): color = "\033[91m"

        print "[" + color + name + "\033[0m] " + text

    pid = os.getpid()
    if ( log_pid != pid ) or ( log_thread == None ):
        log_pid = pid
        log_thread = LogThread(log_dir, main_pid)
        log_thread.start()
    
    log_thread.addItem(name, level, text, pid)

def start(log_level = 0):
    global main_pid, log_dir

    # log level
    if ( log_level != 0 ): setLevel(log_level)

    # check for old logs
    if ( os.path.isdir(log_dir) ):
        files = os.listdir(log_dir)
        if ( len(files) > 0 ):

            # check if old logs already exists
            old_log_dir = os.path.join(log_dir, "old")
            if ( os.path.isdir(old_log_dir) ): utils.rmdir(old_log_dir)
            utils.mkdir(old_log_dir)
            
            for f in files:
                path = os.path.join(log_dir, f)            
                if ( os.path.isdir(path) ): continue            
                os.rename(path, os.path.join(old_log_dir, f))
    else:
        utils.mkdir(log_dir)

    # set the main process id so we know where it began.
    main_pid = os.getpid()

def setLevel(value):
    global log_level
    log_level = value

def getName():
    global names
    source = utils.getSource(3).split(".")[0]
    if ( names.has_key(source) ):
        return names[source]
    return source

def debug(text):
    global log_level
    if ( log_level > 10 ): return
    addItem(getName(), "DEBUG", text, 10)

def info(text):
    global log_level
    if ( log_level > 20 ): return
    addItem(getName(), "INFO", text, 20)

def warning(text):
    global log_level
    if ( log_level > 30 ): return
    addItem(getName(), "WARNING", text, 30)

def error(text):
    global log_level
    if ( log_level > 40 ): return
    addItem(getName(), "ERROR", text, 40)

def critical(text):
    addItem(getName(), "CRITICAL", text, 50)

def fatal(text):
    addItem(getName(), "FATAL", text, 50)

def profile(text):
    addItem("profile", "PROFILE", text)

def alias(source, name):
    global names
    names[source] = name
