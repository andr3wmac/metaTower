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

import os, sys, types, threading, inspect, imp, operator
import mt

class PackageManager:
    def __init__(self):
        self.list = {}

    def get(self, package_name):
        if ( self.list.has_key(package_name) ): return self.list[package_name]
        return None

    def isLoaded(self, package_name):
        return hasattr(self, package_name)

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
            package_path = os.path.join(path, package_name)
            mt.config.load(os.path.join(package_path, "package.cfg"))
            mod.name = mt.config[package_name + "/name"]
            mod.path = path
            mod.id = package_name
            mod.version = mt.config[package_name + "/version"]

            # Load Order, lower numbers get loaded first, 0 is default.
            mod.load_order = mt.config[package_name + "/load_order"]
            if ( not mod.load_order ): mod.load_order = "0"
            mod.load_order = int(mod.load_order)
    
            self.list[package_name] = mod
            setattr(self, package_name, mod)

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
        #for mod_name in package.__includes__:
        #    mod = sys.modules[mod_name]
        #    if ( mod != None ): del sys.modules[mod_name]
            
        #except:
        #    print "Error unloading package: " + package_name

    def unloadAll(self):
        for package in self.list: self.unload(package, False)
        self.list = {}

    def loadDirectory(self, path):        
        files = os.listdir(path)
        if len(files) == 0: return

        load_order = {}
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
                    load_order[package.id] = int(package.load_order)
                
        self.listPackages()        
        
        # after packages are listed, call their load function based on load_order
        sorted_lo = sorted(load_order.iteritems(), key=operator.itemgetter(1))       
        for package_id in sorted_lo:
            package = self.list[package_id[0]]
            if ( hasattr(package, "onLoad") ): package.onLoad()
    
    def listPackages(self):
        print "Packages: "
        output_list = {}
        for packid in self.list:
            package = self.list[packid]
            output_list[package.name] = " - " + package.name + " (" + package.id + " v" + package.version + ")"
        
        # may as well out put them in alphabetical order, looks nice.
        sorted_list = sorted(output_list)
        for key in sorted_list:
            print output_list[key]
        print ""

    def event(self, resp, event, args = {}):
        mt.events.trigger(event, resp, args)
        
    def onLogin(self, resp):
        mt.events.trigger("session.onLogin", resp)
