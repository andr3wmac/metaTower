import httplib, hashlib, time, time, socket, urllib, urllib2
import mt

def onLoad():
    mt.config.load("packages/mtdotnet/users.cfg")

    if ( mt.packages.http ):
        http = mt.packages.http

    # attempt to start the update server.
    try:
        t = UpdateThread()
        t.start()
    except:
        mt.log.error("metaTower.net failed to start.")

    #http.addFile("/search/images/mtfile.png", "packages/search/images/mtfile.png")
    #http.addFile("/search/images/mtfile_trans.png", "packages/search/images/mtfile_trans.png")
    #http.addFile("/search/images/icon.png", "packages/search/images/icon.png")

def home(resp):
    resp.htmlFile("packages/mtdotnet/home.html", "container")
    #resp.jsFile("packages/search/script.js")
    #resp.cssFile("packages/search/style.css")
    #resp.jsFunction("search.setEngines", engine_list)

class UpdateThread( mt.threads.Thread ):
    def __init__(self):
        mt.threads.Thread.__init__(self)
        self.tick_interval = 300

    def tick(self):
        users_list = mt.config.get("mtdotnet/users/user")
        for user in users_list:
            if ( user["auth_url"] == "" ): continue
            try:
                auth_key = mt.utils.uid()

                # We only send the first 16 characters of the password in
                # md5 form. If the password is in text, we convert it first.
                if user["password"]:
                    user["password-md5"] = mt.utils.md5(users[un].password)
                if not user["password-md5"]: continue
                
                # Attempt to update metaTower.net
                values = {
                    "auth_key": auth_key, 
                    "port":     mt.config["http/port"], 
                    "pass":     user["password-md5"][:16]
                }
                http = urllib2.build_opener(urllib2.HTTPRedirectHandler(), urllib2.HTTPCookieProcessor())
                data_out = urllib.urlencode(values)
                response = http.open(user["auth_url"], data_out)

                # Read the response.
                data = response.read()
                resp_args = data.split(":")
                if ( resp_args[0] == "OK" ):
                    mt.log.debug("Authentication for user " + user["username"] + " success.")
                    
                    # check if http is available
                    mt.packages.http.addUser(user["username"], user["password-md5"][16:], auth_key)
                else:
                    mt.log.debug("Authentication for user " + user["username"] + " failed.")

            except Exception as inst:
                mt.log.error("Error updating authentication for " + user["username"] + ": " + str(inst.args))

        # This will save the newly formed password-md5.
        mt.config.save("packages/mtdotnet/users.cfg")
