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
        while True:
            try:
                mt.config["auth_key"] = mtMisc.uid()
                auth_url = mt.config["auth_url"]
                if ( auth_url == "" ): continue

                values = {"auth_key": mt.config["auth_key"], "port": mt.config["port"]}
                http = urllib2.build_opener(urllib2.HTTPRedirectHandler(), urllib2.HTTPCookieProcessor())
                data_out = urllib.urlencode(values)
                response = http.open(auth_url, data_out)

                data = response.read()
                resp_args = data.split(":")
                if ( resp_args[0] == "OK" ):
                    mt.config["remote_ip"] = resp_args[1]    
                    mt.log.debug("Authentication service updated successfully.")
                else:
                    mt.log.debug("Authentication service failed.")

            except Exception as inst:
                mt.log.error("Updating authentication: " + str(inst.args))
            finally:
                last_update = time.time()
            time.sleep(300)

def start():
    try:
        t = UpdateThread()
        t.daemon = True
        t.start()
    except:
        print "Failed to start authentication."
