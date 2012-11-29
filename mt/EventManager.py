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

    def trigger(self, event, *args):
        #print "Triggering event: " + event + " with " + str(len(args)) + " arg(s)"
        result = None
        for e in self.events:
            if e.event == event:
                arg_count = len(inspect.getargspec(e.function).args)
                if ( arg_count == 0 ) : result = e.function()
                if ( arg_count > 0 ):
                    if ( arg_count == len(args) ):
                        result = e.function(*args)
                    if ( arg_count < len(args) ):
                        result = e.function(*args[:(arg_count-len(args))])
        return result
