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

import hashlib, uuid, time, os, mtHTTPServer

sessions = []

class Session():
	auth_key = ""
	last_activity = 0
	events = None
	local = False
	
	def __init__(self):
		self.auth_key = hashlib.sha256(str(uuid.uuid1())).hexdigest()
		self.last_activity = time.time()
		
	def out(self):
		sout = mtHTTPServer.HTTPOut()
		return sout

def newSession():
	ns = Session()
	sessions.append(ns)
	return ns

def findSession(key):
	for session in sessions:
		if ( session.auth_key == key ):
			return session
	return None