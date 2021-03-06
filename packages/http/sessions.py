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

import hashlib, time, os, mt

session_list = []
file_keys = {}

class Session():
    key = ""
    last_activity = 0
    events = None
    local = False
    IP = "127.0.0.1"
    
    def __init__(self):
        self.key = hashlib.sha256(mt.utils.uid()).hexdigest()
        self.last_activity = time.time()
        
    def generateFileKey(self, path):
        global file_keys
        for key in file_keys:
            if ( file_keys[key] == path ):
                return key

        key = mt.utils.uid()
        file_keys[key] = path
        return "*" + key

def new():
    ns = Session()
    session_list.append(ns)
    return ns

def find(key):
    for session in session_list:
        if ( session.key == key ):
            return session
    return None

def fileKey(key):
    global file_keys
    if ( file_keys.has_key(key) ):
        return file_keys[key]
    return None
