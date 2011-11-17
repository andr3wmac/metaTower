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

import mtMisc, inspect

class EventManager:
    class EventItem:
        def __init__(self, event, function, source):
            self.event = event
            self.function = function
            self.source = source

    def __init__(self):
        self.events = []
    
    def register(self, event, function):
        source = mtMisc.getSource()
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

    def trigger(self, event, session = None, args = {}):
        out = None
        if ( session != None ): out = session.out()
        for e in self.events:
            if e.event == event:
                result = None
                arg_count = len(inspect.getargspec(e.function).args)
                if ( arg_count == 0 ) : result = e.function()
                if ( arg_count == 1 ) : result = e.function(session)
                if ( arg_count == 2 ) and ( len(args) > 0 ) : result = e.function(session, args)
                if ( result != None ) and ( out != None ): out.append(result)
        return out
