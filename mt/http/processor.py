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
import mt

def processRequest(httpIn):
    output = mt.http.HTTPOut(httpIn.session)
    
    # Special functions.
    processed = False    
    if ( httpIn.method == "GET" and len(httpIn.path) > 1 ):
        
        # Change user.
        if ( httpIn.path[1] == "@" ):
            login_info = httpIn.path[2:].split(":")

            new_user = None
            if ( len(login_info) == 1 ):
                new_user = verifyUser(httpIn.path[2:], "", httpIn.session.local)
            if ( len(login_info) == 2 ):
                new_user = verifyUser(login_info[0], login_info[1], httpIn.session.local)
            
            if ( new_user != None ): session.user = new_user
            httpIn.path = "/"

        # Execute a command.
        elif ( httpIn.path[1] == "!" ):
            output = processCommand(httpIn.path, httpIn.session)
            processed = True

        # Request a file.
        # The ':' tells metaTower the file search can be anywhere.
        elif ( httpIn.path[1] == ":" ):
            file_parts = os.path.split(httpIn.path[2:])
            output.file(os.path.join(file_parts[0], file_parts[1]))
            processed = True

        # metaTower.js is kept internal in js.py
        # we output it at request.
        elif ( httpIn.path[1:].lower() == "metatower.js" ):
            js_file = mt.js.content
            output.headers["Content-Type"] = "application/javascript"
            output.headers["Content-Length"] = len(js_file)
            output.text_entry = js_file
            processed = True
    
    # if it wasn't a special fucntion send it off
    # to request processor.     
    if ( not processed ):
        mt.requests.process(httpIn, output)

    return output

# Processes a command, often from a package.
def processCommand(path, session):
    cmds = path[2:].split("\n")
    for cmd in cmds:
        try:

            # HTTPOut contains all the functions needed to output data to 
            # the javascript side. Response is included by default on all
            # executed commands.
            response = mt.http.HTTPOut(session)

            # here we 'inject' the response variable into the parms of the
            # command.
            o = cmd.find("(")
            cmd = cmd[:o+1] + "response," + cmd[o+1:]

            # execute and return.
            exec("mt.packages." + cmd)
            return response

        except Exception as inst:
            mt.log.error("Executing command " + path + ": " + str(inst.args))
            return None

# Process login from a client.
def processLogin(client_socket, httpIn):
    path = httpIn.path
    auth_line = httpIn.auth_line

    config = mt.config
    user = None
    resp = None
    login_username = ""
    login_password = ""

    # determine if the packet is local or remote.
    client_addr = client_socket.getpeername()
    local_client = mt.utils.isLocalIP(client_addr[0])
    
    # Check for an auth line that would have came from a POST.
    if ( auth_line != "" ):
        args = auth_line.split(":")
        login_username = args[0]
        login_password = str(hashlib.md5(args[1]).hexdigest())

    # Set security level based on local/remote setting.
    if ( local_client ): security = int(config["local_security"])
    else: security = int(config["remote_security"])

    # Level 0 Security
    #   - Just use default user, no authentication required.
    if ( security == 0 ):
        user = mt.users[config["default_user"]]

    # Level 1 Security
    #   - Prompt user for a username/password if not specific.
    if ( security == 1 ):
        user = verifyUser(login_username, login_password, local_client)
        resp = showLoginForm()

    # Level 2 Security
    #   - Requires the proper auth key from a third party
    #   - Requires a proper username/password for a local user.
    if ( security == 2 ):
        if ( len(path) > 2 ) and ( path[1] == "?" ):
            args = path.split("@")
            key = args[0][2:]
            if ( key == mt.config["auth_key"] ) and ( len(args) > 1 ):
                user_login = args[1].split(":")
                user = mt.users[user_login[0]]
                if (( user != None ) and ( user.password_md5[16:] != user_login[1] )): user = None
        
    # If the user variable is set, login was successful.
    if ( user != None ):
        # Create  new session.
        sesh = mt.sessions.new()
        sesh.user = user
        sesh.IP = client_addr[0]
        sesh.local = local_client
        mt.log.info(user.name + " has logged in.")

        # Create a response variable and
        resp = mt.http.HTTPOut(sesh)
        resp.cookies["session"] = sesh.auth_key
        httpIn.session = sesh

        # Trigger any login events.
        mt.packages.onLogin(resp)
        
        # A proper login can still have a request on the end of it.
        # For instance with a local, no security auto-login.
        # Therefore if the URL contains any commands, we'll pass it
        # back around for execution.
        #if ( path == "/" ):
        resp.append(processRequest(httpIn))
        #elif ( len(path) > 1 ) and (( path[1] == "!" ) or ( path[1] == "@" ) or ( path[1] == "-" ) or ( path[1] == ":" )):
            #resp.append(processRequest(httpIn))
        #else:
            # Clean redirect will remove the auth_key from the URL,
            # it's rather unsightly for the user.
            #resp = sesh.cleanRedirect(resp)
    
    # If resp is None at this point, all login attempts have failed.
    if ( resp == None ):
        resp = mt.http.HTTPOut()
        resp.text("Access denied.")

    return resp

# This function will take the relevant information and see
# if it all matches up. Username/Password(MD5) it will also
# enforce local_only flag on users.
def verifyUser(username, password, local):
    if ( username == None ) or ( username == "" ): return None

    mt.log.info("Login attempt from: " + username)
    if ( mt.users.has_key(username) ):
        user = mt.users[username]
        if ( user.local_only ) and ( not local ): return None
        if ( user.password_md5 == "" ): return user
        if ( mt.users[username].password_md5 == password ): return user
    return None

# this will cause a username/password dialog to popup.
def showLoginForm(key = ""):
    if ( key != "" ): key = "!" + key

    resp = mt.http.HTTPOut()
    resp.status = "401 Forbidden"
    resp.headers["WWW-Authenticate"] = "Basic realm=\"metaTower\""
    return resp

