import os, threading, commands, mt, time
from xml.etree.ElementTree import Element
from QueueController import QueueController

QueueControl = None
last_update = 0

def onLoad():
    global QueueControl

    # load configuration
    mt.config.load("packages/mp3extract/mp3extract.cfg")
    
    # start up our queue monitor.
    QueueControl = QueueController()
    QueueControl.start()

    if ( mt.packages.http ):        
        http = mt.packages.http
        http.addFile("/mp3extract/images/youtube.png", "packages/mp3extract/images/youtube.png")   
        http.addFile("/mp3extract/images/icon.png", "packages/mp3extract/images/icon.png") 

def onUnload():
    global QueueControl

    if ( QueueControl != None ):
        youtube_queue = QueueControl.youtube_queue
        QueueControl.stop()

def add(resp, url):
    global QueueControl

    QueueControl.add(url)
    update(resp)

def remove(resp, uid):
    global QueueControl

    QueueControl.remove(uid)
    update(resp)

def remove_completed(resp):
    global QueueControl
    QueueControl.removeCompleted()
    update(resp)

def home(resp):
    resp.htmlFile("packages/mp3extract/home.html", "container")
    resp.jsFile("packages/mp3extract/script.js")
    resp.cssFile("packages/mp3extract/style.css")

def update(resp):
    global QueueControl
    youtube_queue = QueueControl.youtube_queue

    # Gather data from youtube queue.
    for youtube in youtube_queue:
        try:
            # youtube Removed.
            if ( youtube.removed ):
                resp.js("mp3extract.youtube('" + youtube.uid + "', '" + youtube.title + "', -1);")

            # Queued or Completed
            elif (( youtube.state == 0 ) or ( youtube.state == 3 )):
                resp.js("mp3extract.youtube('" + youtube.uid + "', '" + youtube.title + "', " + str(youtube.state) + ");")

            # Downloading or Converting
            elif (( youtube.state == 1 ) or ( youtube.state == 2 )):
                resp.js("mp3extract.youtube('" + youtube.uid + "', '" + youtube.title + "', " + str(youtube.state) + ", " + str(youtube.progress) + ");")

        except:
            mt.log.error("Error getting status update for youtube.")    
            pass

    # Trigger an update for next time.
    resp.js("mp3extract.update();")

