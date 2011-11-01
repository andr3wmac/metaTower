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

from socket import *
import thread, os, time, sys, Cookie, uuid, hashlib, mtAuth, mimetypes
import mtSession, mtHTTPServer, mtMisc
import mtCore as mt

def processCommand(path, session):
    cmds = path[2:].split("\n")
    for cmd in cmds:
        try:
            # find the open bracket and inject the session variable.
            o = cmd.find("(")
            cmd = cmd[:o+1] + "session," + cmd[o+1:]

            result = ""
            exec("result = mt.packages." + cmd)
            return result
        except Exception as inst:
            mt.log.error("Executing command " + path + ": " + str(inst.args))
            return None

def processRequest(session, request_type, request_path, post_data):
    output = mtHTTPServer.HTTPOut()
    if ( request_type == "GET" ):
        # too short to process.
        if ( len(request_path) < 1 ): return
        
        # either no path given, or trying to relogin on an active session, either go with default command.
        if ( len(request_path) > 1 ) and ( request_path[1] == "-" ):
            session.user.windowmanager = request_path[2:]
            request_path = "/"

        if ( len(request_path) > 1 ) and ( request_path[1] == "@" ):
            login_info = request_path[2:].split(":")

            new_user = None
            if ( len(login_info) == 1 ):
                new_user = userLogin(request_path[2:], "", session.local)
            if ( len(login_info) == 2 ):
                new_user = userLogin(login_info[0], login_info[1], session.local)
            
            if ( new_user != None ): session.user = new_user
            request_path = "/"

        if ( request_path == "/" ) or ( request_path[1] == "?" ):
            output = mt.events.trigger(session.user.windowmanager + ".onIndex", session)
        elif ( request_path[1] == "!" ):
            output = processCommand(request_path, session)
        elif ( request_path[1] == ":" ):
            output = session.out()
            file_parts = os.path.split(request_path[2:])
            output.file(file_parts[1], file_parts[0])
        else:
            output = session.out()
            output.file(request_path[1:])
                
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
            mt.events.trigger("upload_success_" + form_name, session)
    return output

def processLogin(socket, path, auth_line):
    config = mt.config
    user = None
    sout = None
    login_username = ""
    login_password = ""
    key = ""

    # determine if the packet is local or remote.
    local_client = False
    client_addr = socket.getpeername()
    if ( str(client_addr[0])[:7] == "192.168" ) or ( str(client_addr[0]) == "127.0.0.1" ) or ( str(client_addr[0])[:5] == "10.0." ):
        local_client = True
    
    # see if we have post data.
    if ( auth_line != "" ):
        args = auth_line.split(":")
        login_username = args[0]
        login_password = str(hashlib.md5(args[1]).hexdigest())

    # check if we have a usable key
    key_ok = False
    if ( len(path) > 2 ) and ( path[1] == "?" ):
        args = path.split("@")
        key = args[0][2:]
        if ( key == mt.config["auth_key"] ) and ( len(args) > 1 ):
            user_login = args[1].split(":")
            login_username = user_login[0]
            login_password = user_login[1]
            key_ok = True

    # security.
    if ( local_client ): security = int(config["local_security"])
    else: security = int(config["remote_security"])

    if ( security == 0 ):
        user = mt.users[config["default_user"]]

    if ( security == 1 ):
        user = userLogin(login_username, login_password, local_client)
        sout = showLoginForm()

    if ( security == 2 ):
        if ( key_ok ): 
            user = userLogin(login_username, login_password, local_client)
            sout = showLoginForm(key)
        
    if ( user != None ):
        print "User logged in."
        sesh = mtSession.newSession()
        sesh.user = user
        sesh.local = local_client
        mt.packages.onLogin(sesh)
        sout = sesh.out()
        sout.cookies["session"] = sesh.auth_key
        if ( len(path) > 1 ) and (( path[1] == "!" ) or ( path[1] == "@" ) or ( path[1] == "-" ) or ( path[1] == ":" )):
            sout.append(processRequest(sesh, "GET", path, ""))
        else:
            sout = sesh.cleanRedirect(sout)
    
    if ( sout == None ):
        sout = mtHTTPServer.HTTPOut()
        sout.text("Access denied.")

    return sout

def userLogin(username, password, local):
    if ( username == None ) or ( username == "" ): return None

    print "Login attempt from: " + username + " pass: " + password
    if ( mt.users.has_key(username) ):
        user = mt.users[username]
        if ( user.local_only ) and ( not local ): return None
        if ( user.password_md5 == "" ): return user
        if ( mt.users[username].password_md5 == password ): return user
    return None

def showLoginForm(key = ""):
    if ( key != "" ): key = "!" + key

    output = mtHTTPServer.HTTPOut()
    output.status = "401 Forbidden"
    output.headers["WWW-Authenticate"] = "Basic realm=\"metaTower\""
    #output.textOut += "<html><form method='POST' action='" + key + "'>"
     #output.textOut += "Username: <input type='text' name='user' size='15' /><br />Password: <input type='password' name='pass' size='15' /><br />"
      #output.textOut += "<div align='center'><p><input type='submit' value='Login' /></p></div></form></html>"
    
    return output
