import time
import mtCore as mt

def onLoad():
	mt.events.register("jman.onIndex", onIndex)
	mt.events.register("jman.onPageLoad", onPageLoad)

def onUnload():
	mt.events.clear(onIndex)
	mt.events.clear(onPageLoad)

def onIndex(session):
	session.jman_menu = []
	out = session.out()
	out.file("jman/index.html")
	return out
	
def onPageLoad(session):
	out = session.out()
	out.append(mt.events.trigger("jman.load", session))
	menuJS = ""
	for entry in session.jman_menu:
		menuJS += "jman.menu('" + entry.caption + "', " + str(entry.data) + ");"
	out.js(menuJS)
	return out

class MenuEntry:
	caption = ""
	data = {}

def menu(session, caption, data):
	entry = MenuEntry()
	entry.caption = caption
	entry.data = data
	session.jman_menu.append(entry)
