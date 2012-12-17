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

import thread, os, time, sys, Cookie, uuid, hashlib, mimetypes
import mt, sessions

def processRequest(httpIn, httpOut):
    #output = http.HTTPOut(httpIn.session)
    
    # Special functions.
    processed = False    
    if ( httpIn.method == "GET" and len(httpIn.path) > 1 ):

        # Execute a command.
        if ( httpIn.path[1] == "!" ):
            processCommand(httpIn, httpOut)
            processed = True

        # Request a file.
        # The ':' tells metaTower the file search can be anywhere.
        elif ( httpIn.path[1] == ":" ):
            file_parts = os.path.split(httpIn.path[2:])
            httpOut.file(os.path.join(file_parts[0], file_parts[1]))
            processed = True
        
        # metaTower.js
        elif ( httpIn.path[1:].lower() == "metatower.js" ):
            httpOut.file("packages/http/metaTower.js")
            processed = True
    
    # if it wasn't a special function send it off to request processor.     
    if ( not processed ):
        mt.events.trigger("HTTP GET " + httpIn.path, httpIn, httpOut)

    # still not processed? 404.
    if ( not processed ):
        httpOut.status = "404 Not Found"

# Processes a command, often from a package.
def processCommand(httpIn, httpOut):
    cmds = httpIn.path[2:].split("\n")
    for cmd in cmds:
        try:

            # HTTPOut contains all the functions needed to output data to 
            # the javascript side. Response is included by default on all
            # executed commands.

            # here we 'inject' the response variable into the parms of the
            # command.
            o = cmd.find("(")
            cmd = cmd[:o+1] + "httpOut," + cmd[o+1:]

            # execute and return.
            exec("mt.packages." + cmd)

        except Exception as inst:
            mt.log.error("Executing command " + httpIn.path + ": " + str(inst.args))
            return None

# Process login from a client.
def processLogin(client_socket, httpIn, httpOut):
    path = httpIn.path
    allow_login = False
    clean_redirect = False
    login = {
        "username": "",
        "password": "",
        "key": "",
        "local": False
    }

    # determine if the packet is local or remote.
    client_addr = client_socket.getpeername()
    login["local"] = mt.utils.isLocalIP(client_addr[0])
    
    # Check for an auth line that would have came from a POST.
    if ( httpIn.auth_line != "" ):
        args = httpIn.auth_line.split(":")
        login["username"] = args[0]
        login["password"] = str(hashlib.md5(args[1]).hexdigest())

    # Check if we have a login path
    if ( len(path) > 2 ) and ( path[1] == "?" ):
        args = path.split("@")
        login["key"] = args[0][2:]
        login_data = args[1].split(":")
        login["username"] = login_data[0]
        login["password"] = login_data[1]
        clean_redirectdirect = True

    # Set security level based on config.
    security = int(mt.config["http/security"])

    if ( security < 2 and login["local"] ):
        allowLogin = True

    # Level 0 Security
    #   - Allow all logins.
    if ( security == 0 ):
        allowLogin = True

    # Level 1 Security
    #   - All local client allows, username/password for remote.
    if ( security == 1 ):
        if login["local"]:
            allowLogin = True
        else:
            allowLogin = verifyUser(login)

    # Level 2 Security
    #   - Requires the proper login from both.
    if ( security == 2 ):
        allowLogin = verifyUser(login)

    # If we're allowed to login:
    if allowLogin:
        # Create  new session.
        sesh = sessions.new()
        sesh.IP = client_addr[0]
        sesh.local = login["local"]

        # Create a response variable and
        httpIn.session = sesh
        httpOut.cookies["session"] = sesh.key
        httpOut.session = sesh

        #resp = sesh.clean_redirectdirect(resp)
        if ( clean_redirectdirect ):
            httpOut.status = "302 Found"
            httpOut.headers["Location"] = "http://" + httpIn.host + "/"
            httpOut.headers["Content-Length"] = "0"
        else:
            processRequest(httpIn, httpOut)
    else:
        httpOut.text("Access denied.")
    
# This function will take the relevant information and see
# if it all matches up. Username/Password(MD5) it will also
# enforce local_only flag on users.
def verifyUser(login):
    user = mt.packages.http.getUser(login["username"])
    if ( not user == None ):
        if ( user.password == login["password"] and user.key == login["key"] ):
            return True
    return False

# this will cause a username/password dialog to popup.
def showLoginForm(httpOut):
    httpOut.status = "401 Forbidden"
    httpOut.headers["WWW-Authenticate"] = "Basic realm=\"metaTower\""
