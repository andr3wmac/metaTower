"""
 * metaTower v0.4.0
 * http://www.metatower.com
 *
 * Copyright 2011, Andrew MacIntyre
 * http://www.andrewmac.ca
 * Licensed under GPL v3.
 * See license.txt 
 *  or http://www.metatower.com/license.txt
"""

import mt, inspect

class EventManager:
    class EventItem:
        def __init__(self, event, function, source):
            self.event = event
            self.function = function
            self.source = source

    def __init__(self):
        self.events = []
    
    def register(self, event, function):
        source = mt.utils.getSource()
        newEvent = self.EventItem(event, function, source)
        self.events.append(newEvent)

    def clear(self, function = None):
        if ( function == None ): self.events = []
        else:
            new_list = []
            for e in self.events:
                if e.function != function: new_list.append(e)
            self.events = new_list

    def clearSource(self, source):
        new_list = []
        for e in self.events:
            if e.source != source: new_list.append(e)
        self.events = new_list

    def trigger(self, event, resp = None, args = {}):
        result = None
        for e in self.events:
            if e.event == event:
                arg_count = len(inspect.getargspec(e.function).args)
                if ( arg_count == 0 ) : result = e.function()
                if ( arg_count == 1 ) : result = e.function(resp)
                if ( arg_count == 2 ) and ( len(args) > 0 ) : result = e.function(resp, args)
        return result