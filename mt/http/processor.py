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

import thread, os, time, sys, Cookie, uuid, hashlib, mimetypes
import mt

def processRequest(session, request_type, request_path, post_data):
    output = mt.http.HTTPOut(session)

    # GET Request
    if ( request_type == "GET" ):
        # too short to process.
        if ( len(request_path) < 1 ): return
        
        # These commands allow the user to change user/window
        # managers therefore they need to be executed first.
        if ( len(request_path) > 1 ):
            # Change window manager.
            if ( request_path[1] == "-" ):
                session.user.windowmanager = request_path[2:]
                request_path = "/"

            # Change user.
            elif ( request_path[1] == "@" ):
                login_info = request_path[2:].split(":")

                new_user = None
                if ( len(login_info) == 1 ):
                    new_user = verifyUser(request_path[2:], "", session.local)
                if ( len(login_info) == 2 ):
                    new_user = verifyUser(login_info[0], login_info[1], session.local)
                
                if ( new_user != None ): session.user = new_user
                request_path = "/"

        # '/' = default request
        # '/?' = Login key, useless at this point we're already logged in.
        if ( request_path == "/" ) or ( request_path[1] == "?" ):
            mt.events.trigger(session.user.windowmanager + ".onIndex", output)

        # Execute a command.
        elif ( request_path[1] == "!" ):
            output = processCommand(request_path, session)

        # Request a file.
        # The ':' tells metaTower the file search can be anywhere.
        elif ( request_path[1] == ":" ):
            file_parts = os.path.split(request_path[2:])
            output.file(file_parts[1], file_parts[0])

        # metaTower.js is kept internal in js.py
        # we output it at request.
        elif ( request_path[1:].lower() == "metatower.js" ):
            js_file = mt.js.content
            output.headers["Content-Type"] = "application/javascript"
            output.headers["Content-Length"] = len(js_file)
            output.text_entry = js_file

        # anything else process like a file request.
        # unlike ':' the search is in packages/ folders
        else:
            output.file(request_path[1:])
                
    # POST Request
    if ( request_type == "POST" ):
        post_args = post_data.splitlines()
        
        content_type = ""
        form_name = ""
        file_name = ""
        file_data = ""
        
        x = 1
        while x < len(post_args):
            line = post_args[x]
            if ( line[0:20] == "Content-Disposition:" ):
                args = line.split('"')
                form_name = args[1]
                file_name = args[3]
            if ( line[0:14] == "Content-Type: " ):
                content_type = line
            if (( file_name != "" ) and ( line == "" )):
                file_data = post_data.split(content_type + "\r\n\r\n")[1]
                file_data = file_data[0:len(file_data)-4]
                break
                
            x += 1
                
        if (( file_name != "" ) and ( file_data != "" )):
            if ( request_path == "/" ): request_path = "files/upload/"
            else: request_path = request_path[1:]
            f = open(os.path.join(request_path, file_name), "wb")
            f.write(file_data)
            f.close()
            output = session.out()
            output.text("Upload successful.")
            mt.events.trigger("upload_success_" + form_name, output)
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
def processLogin(client_socket, path, auth_line):
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

        # Trigger any login events.
        mt.packages.onLogin(resp)
        
        # A proper login can still have a request on the end of it.
        # For instance with a local, no security auto-login.
        # Therefore if the URL contains any commands, we'll pass it
        # back around for execution.
        if ( len(path) > 1 ) and (( path[1] == "!" ) or ( path[1] == "@" ) or ( path[1] == "-" ) or ( path[1] == ":" )):
            resp.append(processRequest(sesh, "GET", path, ""))
        else:
            # Clean redirect will remove the auth_key from the URL,
            # it's rather unsightly for the user.
            resp = sesh.cleanRedirect(resp)
    
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

