"""
 * metaTower v0.3.1
 * http://www.metatower.com
 *
 * Copyright 2011, Andrew W. MacIntyre
 * http://www.andrewmac.ca
 * Licensed under GPL v3.
 * See license.txt 
 *  or http://www.metatower.com/license.txt
"""

import httplib, hashlib, uuid, time, threading, time, mtSession, socket, urllib, urllib2, mtHTTPServer, mtMisc
import mtCore as mt
last_update = 0

class User():
    def __init__(self):
        self.name = ""
        self.password_md5 = ""
        self.password = ""
        self.homedir = ""
        self.windowmanager = ""
        self.auth_url = ""
        self.local_only = False

class UpdateThread( threading.Thread ):
    def run ( self ):
        global last_update
        while mt.running:
            if ( time.time() - last_update > 300 ):
                try:
                    mt.config["auth_key"] = mtMisc.uid()
                    for username in mt.users:
                        user = mt.users[username]
                        if ( user.auth_url == "" ): continue

                        values = {"username": user.name, "auth_key": mt.config["auth_key"], "port": mt.config["port"]}
                        http = urllib2.build_opener(urllib2.HTTPRedirectHandler(), urllib2.HTTPCookieProcessor())
                        data_out = urllib.urlencode(values)
                        response = http.open(user.auth_url, data_out)
                        data = response.read()
                        mt.log.debug("Authentication response for " + user.name + ": " + data)
                except Exception as inst:
                    mt.log.error("Updating authentication: " + str(inst.args))
                finally:
                    last_update = time.time()
            time.sleep(1)

def start():
    try:
        t = UpdateThread()
        t.start()
    except:
        print "Failed to start authentication."
