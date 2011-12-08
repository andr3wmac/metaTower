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

import ConfigParser, os, sys, logging, hashlib, uuid, time, inspect, urllib
import mtAuth, mtConfigManager, mtEventManager, mtPackageManager, mtMisc, mtLogManager
import mtHTTPServer, mtAuth

restart = False
running = False
log = None
config = None
users = {}
events = None
packages = None
login_tickets = {}

def start(version):
    global running, config, log, users, packages, events, http_running

    # intro
    print "metaTower v" + version + "\n"

    # logging system
    log = mtLogManager.LogManager()
    log.alias("mtAuth", "auth")
    log.alias("mtHTTPServer", "network")
    log.alias("mtHTTPProcessor", "network")

    # load initial configurations
    config = mtConfigManager.ConfigManager()
    config.load("metaTower.cfg")
    config.load("users.cfg")
    
    # load users.
    users_list = config.get("users/user")
    for user in users_list:
        un = user["name"]
        users[un] = mtAuth.User()
        users[un].name = un
        users[un].password_md5 = user["password-md5"]

        # load the homedir, and create it if it doesn't exist.
        users[un].homedir = user["home"]
        mtMisc.mkdir(users[un].homedir)

        users[un].windowmanager = user["windowmanager"]
        users[un].auth_url = user["auth_url"]
        if ( user["local_only"] != "" ): users[un].local_only = True

    # events
    events = mtEventManager.EventManager()

    # packages
    packages = mtPackageManager.PackageManager()
    packages.loadDirectory("packages")

    # determine ip addresses.
    print "\nYou can connect to your tower at:"

    #  - local
    config["local_ip"] = mtMisc.getLocalIP()
    if ( not config["local_ip"].startswith("127.") ): print " http://127.0.0.1:" + config["port"] + "/"
    print " http://" + config["local_ip"] + ":" + config["port"] + "/"
    running = True

    mtHTTPServer.start()
    mtAuth.start()
        
def stop():
    global running, config, packages, http_running
    packages.unloadAll()
    config.save()
    mtHTTPServer.stop()
    running = False

def restart():
    global restart
    stop()
    restart = True
