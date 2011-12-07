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

import os, sys, types, threading, inspect, imp
import mtCore as mt

class PackageManager:
    def __init__(self):
        self.list = {}

    def get(self, package_name):
        if ( self.list.has_key(package_name) ): return self.list[package_name]
        return None

    def load(self, package_name, path = ""):
        # if the package is already a module, we'll just use it.
        # this could indicate it was disabled.
        if ( sys.modules.has_key(package_name) ):
            return self.reload(package_name)
        else:
            #syspath = os.path.join(os.getcwd(), path)
            #if ( not syspath in sys.path ): sys.path.append(syspath)
            #if ( not path in sys.path ): sys.path.append(path)

            # first we take down a list of loaded modules.
            mods = []
            for mod_name in sys.modules: mods.append(mod_name)

            # import our new modules.
            #mod = __import__(package_name, globals(), locals(), [''])
            fp, pathname, description = imp.find_module(package_name, [path])
            mod = imp.load_module(package_name, fp, pathname, description)

            # now figure out the difference.
            mod.__includes__ = []

            for mod_name in sys.modules:
                if ( not mod_name in mods ): mod.__includes__.append(mod_name)

        # load config files if they aren't already.
        if ( not mt.config.contains(package_name) ):
            mt.config.load(os.path.join(path, package_name, "package.cfg"))
            mod.name = mt.config[package_name + "/name"]
            mod.path = path
            mod.id = package_name
            mod.version = mt.config[package_name + "/version"]

            self.list[package_name] = mod
            setattr(self, package_name, mod)
            if ( hasattr(mod, "onLoad") ): mod.onLoad()

        return mod

    def reload(self, package_name):
        package = None
        package = self.get(package_name)
        path = package.path
    
        self.unload(package_name)
        package = self.load(package_name, path)
        return package

    def unload(self, package_name, pop = True):
        #try:
        package = self.list[package_name]

        # remove the module.
        if ( pop ): self.list.pop(package_name)
        if ( hasattr(package, "onUnload") ): package.onUnload()
        if ( hasattr(self, package_name) ): delattr(self, package_name)

        # clear from events/config
        mt.config.clear(package_name)
        mt.events.clearSource(package_name)

        # finally delete it.
        for mod_name in package.__includes__:
            mod = sys.modules[mod_name]
            if ( mod != None ): del sys.modules[mod_name]
            
        #except:
        #    print "Error unloading package: " + package_name

    def unloadAll(self):
        for package in self.list: self.unload(package, False)
        self.list = {}

    def loadDirectory(self, path):        
        files = os.listdir(path)
        if len(files) == 0: return

        for f in files:
            package_path = os.path.join(path,f)
            if ( os.path.isdir(package_path) ):
                package_files = os.listdir(package_path)

                has_init = False
                has_cfg = False
                if len(package_files) > 0:
                    for af in package_files:
                        if af == "__init__.py": has_init = True
                        if af == "package.cfg": has_cfg = True

                if ( has_init ) and ( has_cfg ):
                    package = self.load(f, path)
                
        self.listPackages()        
    
    def listPackages(self):
        print "Packages: "
        for packid in self.list:
            package = self.list[packid]
            print " - " + package.name + " (" + package.id + " v" + package.version + ")"

    def event(self, resp, event, args = {}):
        mt.events.trigger(event, resp, args)
        
    def pageLoaded(self, resp):
        mt.events.trigger(resp.session.user.windowmanager + ".onPageLoad", resp)

    def onLogin(self, resp):
        mt.events.trigger("session.onLogin", resp)
