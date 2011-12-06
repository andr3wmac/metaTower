"""
 * metaTower v0.3.5
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

running = False
restart = False
log = None
config = None
users = {}
events = None
packages = None
login_tickets = {}

def start():
    global running, config, log, users, packages, events

    # load initial configurations
    running = True
    config = mtConfigManager.ConfigManager()
    config.load("metaTower.xml")
    config.load("users.xml")
    
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
        
    # logging system
    log = mtLogManager.LogManager()

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

    #  - remote
    try:
        config["remote_ip"] = urllib.urlopen('http://whatismyip.org').read()
        print " http://" + config["remote_ip"] + ":" + config["port"] + "/"
    except:
        pass
        
def stop():
    global running, config, packages
    running = False
    packages.unloadAll()
    config.save()
    sys.exit(0)

def restart():
    global restart
    stop()
    restart = True
    raise Exception
