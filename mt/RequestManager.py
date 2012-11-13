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

import mt, inspect

class RequestManager:
    class FnRequest:
        def __init__(self, method, path, function, source):
            self.method = method
            self.path = path
            self.function = function
            self.source = source

    class FileRequest:
        def __init__(self, method, path, file_path, source):
            self.method = method
            self.path = path
            self.file_path = file_path
            self.source = source

    def __init__(self):
        self.fn_requests = []
        self.file_requests = []    

    def addFunction(self, method, path, function):
        source = mt.utils.getSource()
        newFnRequest = self.FnRequest(method, path, function, source)
        self.fn_requests.append(newFnRequest)

    def addFile(self, method, path, file_path):
        source = mt.utils.getSource()
        newFileRequest = self.FileRequest(method, path, file_path, source)
        self.file_requests.append(newFileRequest)

    def clear(self, function = None):
        if ( function == None ): self.fn_requests = []
        else:
            new_list = []
            for e in self.fn_requests:
                if e.function != function: new_list.append(e)
            self.fn_requests = new_list

    def clearSource(self, source):
        new_list = []
        for e in self.fn_requests:
            if e.source != source: new_list.append(e)
        self.fn_requests = new_list

    def process(self, httpIn, resp = None):
        #print "PROCESSING: " + httpIn.method + " " + httpIn.path

        result = None
        processed = False
        for e in self.fn_requests:
            if ((e.path == httpIn.path) and (e.method == httpIn.method)):
                arg_count = len(inspect.getargspec(e.function).args)
                if ( arg_count == 0 ) : result = e.function()
                if ( arg_count == 1 ) : result = e.function(resp)
                if ( arg_count == 2 ) : result = e.function(resp, httpIn)
                processed = True

        if ( not processed ):
            for f in self.file_requests:
                if ((f.path == httpIn.path) and (f.method == httpIn.method)):          
                    resp.file(f.file_path)
                    result = resp
        
        return result
