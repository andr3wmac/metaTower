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

import ConfigParser, os, sys, logging, hashlib, time, inspect, urllib
import ConfigManager, EventManager, PackageManager
import utils, log, threads

restart = False
config = None
events = None
packages = None
users = {}

login_tickets = {}

def start(version, log_level, profiling):
    global running, config, users, packages, events

    # intro
    print "metaTower v" + version + "\n"

    # profiling
    utils.setProfiling(profiling)

    # logging system
    log.start(log_level)

    # load initial configurations
    config = ConfigManager.ConfigManager()

    # events
    events = EventManager.EventManager()

    # packages
    packages = PackageManager.PackageManager()
    packages.loadDirectory("packages")

    return True
        
def stop():
    global running, config, packages
    print "Shutting down.."
    packages.unloadAll()
    config.save()
    threads.stopAll()

def restart():
    global restart
    stop()
    restart = True

def echo(text):
    src = utils.getSource()
    print "[" + src + "] " + text
