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

import logging, threads, time, os, utils, multiprocessing

class LogItem:
    def __init__(self, source, level, data, pid):
        self.source = source
        self.level = level
        self.data = data
        self.pid = pid

class LogThread(threads.Thread):
    def __init__(self, log_dir):
        threads.Thread.__init__(self)
        self.queue = multiprocessing.Queue()
        self.log_dir = log_dir

    def run(self):
        file_handles = {}
        try:
            while self.running:
                try:
                    item = self.queue.get_nowait()
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
log_thread = None
names = {};

def addItem(name, level, text):
    global log_thread, log_pid, log_dir

    pid = os.getpid()
    if ( log_pid != pid ) or ( log_thread == None ):
        log_pid = pid
        log_thread = LogThread(log_dir)
        log_thread.start()
    
    log_thread.addItem(name, level, text, pid)

def clearLogs():
    global log_dir
    utils.rmdir(log_dir)
    utils.mkdir(log_dir)

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
    addItem(getName(), "DEBUG", text)

def info(text):
    global log_level
    if ( log_level > 20 ): return
    addItem(getName(), "INFO", text)

def warning(text):
    global log_level
    if ( log_level > 30 ): return
    addItem(getName(), "WARNING", text)

def error(text):
    global log_level
    if ( log_level > 40 ): return
    addItem(getName(), "ERROR", text)

def critical(text):
    addItem(getName(), "CRITICAL", text)

def fatal(text):
    addItem(getName(), "FATAL", text)

def profile(text):
    addItem("profile", "PROFILE", text)

def alias(source, name):
    global names
    names[source] = name
