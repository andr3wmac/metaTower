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

import inspect, uuid

def uid():
    return str(uuid.uuid1()).replace("-", "")

def getSource(depth=2):
    try:
        frm = inspect.stack()[depth]
        mod = inspect.getmodule(frm[0])
        source = mod.__name__
        if ( source.endswith(".") ): source = source[:len(source)-1]
    except:
        source = ""
    return source
