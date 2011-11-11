"""
 * metaTower v0.3.2
 * http://www.metatower.com
 *
 * Copyright 2011, Andrew W. MacIntyre
 * http://www.andrewmac.ca
 * Licensed under GPL v3.
 * See license.txt 
 *  or http://www.metatower.com/license.txt
"""

import ConfigParser, os, sys, mtAuth, logging, mtCore
import xml.etree.ElementTree as ElementTree
import xml.dom.minidom as xml

class ConfigManager:
    class ConfigItem(str):
        def __init__(self, value, target = None):
            super( str, self ).__init__()
            self.name = ""
            self.path = ""
            self.source_file = ""
            self.attrib = {}

        def __getitem__(self, key):
            if ( self.attrib.has_key(key) ): return self.attrib[key]
            else: return ""

        def __setitem__(self, key, value):
            self.attrib[key] = value

        def copy(self, target):
            self.name = target.name
            self.path = target.path
            self.source_file = target.source_file
            self.attrib = target.attrib

    def __init__(self):
        self.items = []

    def _loadTree(self, tree, path = "", filename = ""):
        for a in tree: 
            item_text = ""
            if ( a.text ): item_text = a.text.strip()

            item = self.ConfigItem(item_text)
            item.name = a.tag
            item.path = path + a.tag
            item.attrib = a.attrib
            item.source_file = filename
            
            if ( item != "" ) or ( len(item.attrib) > 0 ):
                self.items.append(item)
            self._loadTree(a, path + a.tag + "/", filename)
    
    def load(self, filename):
        try:
            newTree = ElementTree.ElementTree()
            newTree.parse(filename)
            self._loadTree(newTree.getroot(), "", filename)
        except Exception as inst:
            mtCore.log.error("Error loading config file " + filename + ": " + str(inst.args))

    def loadString(self, data, filename = ""):
        newTree = ElementTree.fromstring(data)
        self._loadTree(newTree, "", filename)

    def add(self, item, path, filename = ""):
        p_args = path.split("/")
        item.name = p_args[len(p_args)-1]
        item.path = path
        item.source_file = filename
        self.items.append(item)

    def get(self, key, filename = ""):
        results = []
        for item in self.items:
            if ( item.path == key ): 
                if ( filename == "" ) or ( item.source_file == filename ):
                    results.append(item)
        return results

    def clear(self, key, filename = ""):
        new_tree = []
        for item in self.items:
            if ( not item.path.startswith(key) ) :
                new_tree.append(item)
            else:
                if ( filename != "" ) and ( not item.source_file == filename ):
                    new_tree.append(item)
        self.items = new_tree

    def contains(self, key):
        for item in self.items:
            if ( item.path.startswith(key + "/") ) or ( item.path == key ): return True
        return False

    def __getitem__(self, key):
        result = self.get(key)
        if ( len(result) == 0 ): return self.ConfigItem("")
        return result[len(result)-1]
            
    def __setitem__(self, key, value):
        # check to see if it already exists.
        result = self.get(key)
        # if not, create it.
        if ( len(result) == 0 ): 
            item = self.ConfigItem(value)
            self.add(item, key)
            return

        # looks like we found it.
        item = result[len(result)-1]

        if ( value.__class__.__name__ == "ConfigItem" ):       
            index = self.items.index(item)
            self.items[index] = value
            return
 
        if ( value.__class__.__name__ == "str" ):
            new_item = self.ConfigItem(value)
            new_item.copy(item)
            index = self.items.index(item)
            self.items[index] = new_item
            return

    def save(self, filename = ""):
        if ( filename == "" ):
            already_saved = []
            for item in self.items:
                if ( item.source_file != "" ) and ( not item.source_file in already_saved ):
                    self.save(item.source_file)
                    already_saved.append(item.source_file)
        else:
            root = ElementTree.Element("metaTower")
            tree = ElementTree.ElementTree(root)

            trees_out = {}
            for item in self.items:
                if ( item.source_file == "" ): continue
                if ( not trees_out.has_key(item.source_file) ):
                    trees_out[item.source_file] = ElementTree.Element("metaTower")

                el = trees_out[item.source_file]
                elements = item.path.split("/")
                for e in elements: 
                    ol = el.find(e)
                    if ( ol != None ): 
                        attrib_match = True
                        for attr in item.attrib:
                            if ( ol.attrib.has_key(attr) ) and ( item.attrib[attr] != ol.attrib[attr] ): attrib_match = False
                        for attr in ol.attrib:
                            if ( item.attrib.has_key(attr) ) and ( item.attrib[attr] != ol.attrib[attr] ): attrib_match = False                    
                        if ( attrib_match ): 
                            el = ol
                            continue
                    newe = ElementTree.Element(e)
                    el.append(newe)
                    el = newe

                el.text = item
                el.attrib = item.attrib

            for tree in trees_out:
                try:
                    prettyxml = xml.parseString(ElementTree.tostring(trees_out[tree])).toprettyxml()
                    f = open(tree, 'w')
                    f.write(prettyxml)
                    f.close()
                except:
                    pass

    
