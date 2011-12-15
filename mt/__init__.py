"""
 * metaTower v0.4.0
 * http://www.metatower.com
 *
 * Copyright 2011, Andrew MacIntyre
 * http://www.andrewmac.ca
 * Licensed under GPL v3.
 * See license.txt 
 *  or http://www.metatower.com/license.txt
"""

import ConfigParser, os, sys, logging, hashlib, uuid, time, inspect, urllib
import ConfigManager, EventManager, PackageManager
import auth, http, utils, log, sessions, js

restart = False
running = False
config = None
events = None
packages = None
users = {}

login_tickets = {}

def start(version, log_level, profiling):
    global running, config, users, packages, events, http_running

    # intro
    print "metaTower v" + version + "\n"

    # profiling
    utils.setProfiling(profiling)

    # logging system
    log.setLevel(log_level)
    log.alias("mtAuth", "auth")
    log.alias("mtHTTPServer", "network")
    log.alias("mtHTTPProcessor", "network")

    # load initial configurations
    config = ConfigManager.ConfigManager()
    config.load("metaTower.cfg")
    config.load("users.cfg")
    
    # load users.
    users_list = config.get("users/user")
    for user in users_list:
        un = user["name"]
        users[un] = auth.User()
        users[un].name = un
        users[un].password_md5 = user["password-md5"]

        # load the homedir, and create it if it doesn't exist.
        users[un].homedir = user["home"]
        utils.mkdir(users[un].homedir)

        users[un].windowmanager = user["windowmanager"]
        users[un].auth_url = user["auth_url"]
        if ( user["local_only"] != "" ): users[un].local_only = True

    # events
    events = EventManager.EventManager()

    # packages
    packages = PackageManager.PackageManager()
    packages.loadDirectory("packages")

    # determine ip addresses.
    print "\nHit Enter at anytime to shutdown."
    print "You can connect to your tower at:"

    #  - local
    config["local_ip"] = utils.getLocalIP()
    if ( not config["local_ip"].startswith("127.") ): print " http://127.0.0.1:" + config["port"] + "/"
    print " http://" + config["local_ip"] + ":" + config["port"] + "/"
    running = True

    http.start()
    auth.start()
        
def stop():
    global running, config, packages, http_running
    print "Shutting down.."
    packages.unloadAll()
    config.save()
    http.stop()
    running = False

def restart():
    global restart
    stop()
    restart = True
