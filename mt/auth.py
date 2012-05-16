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

import httplib, hashlib, time, time, socket, urllib, urllib2
import mt, threads

class User():
    def __init__(self):
        self.name = ""
        self.password_md5 = ""
        self.password = ""
        self.homedir = ""
        self.windowmanager = ""
        self.auth_url = ""
        self.local_only = False

class UpdateThread( threads.Thread ):
    def __init__(self):
        threads.Thread.__init__(self)
        self.tick_interval = 300

    def tick(self):
        # check if we have a remote_ip
        if ( mt.config["remote_ip"] == "" ):
            # Fetch the remote_ip
            remote_url = "https://www.metatower.net/ip.php"
            try:
                mt.config["remote_ip"] = urllib.urlopen(remote_url).read()
                print " http://" + mt.config["remote_ip"] + ":" + mt.config["port"] + "/"
            except:
                mt.log.error("Could not fetch remote_ip from: " + remote_url)

        # update the authentication.
        mt.config["auth_key"] = mt.utils.uid()
        for username in mt.users:
            user = mt.users[username]
            if ( user.auth_url != "" ):
                try:
                    upass = ""
                    if ( user.password_md5 != "" ):
                        upass = user.password_md5[:16]

                    values = {"auth_key": mt.config["auth_key"], "port": mt.config["port"], "pass": upass }
                    http = urllib2.build_opener(urllib2.HTTPRedirectHandler(), urllib2.HTTPCookieProcessor())
                    data_out = urllib.urlencode(values)
                    response = http.open(user.auth_url, data_out)

                    data = response.read()
                    resp_args = data.split(":")
                    if ( resp_args[0] == "OK" ):
                        mt.config["remote_ip"] = resp_args[1]
                        mt.log.debug("Authentication for user " + user.name + " success.")
                    else:
                        mt.log.debug("Authentication for user " + user.name + " failed.")

                except Exception as inst:
                    mt.log.error("Error updating authentication for " + user.name + ": " + str(inst.args))

def start():
    try:
        t = UpdateThread()
        t.start()
    except:
        print "Failed to start authentication."
