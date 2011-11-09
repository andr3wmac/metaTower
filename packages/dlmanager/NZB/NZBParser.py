from xml.sax import parse as saxParse
from xml.sax import parseString as saxParseString
from xml.sax import handler,SAXException
import logging

log = logging.getLogger("NZBParser")

class NZBParser(handler.ContentHandler):
    def __init__(self):
        self.path = []   # stack for tracking our current xml path
        self.files = []  # a list of all the files in the nzb post
    def xpath(self):
        return "/".join( self.path )
    def startElement(self,tag,attrs):
        self.path.append( tag )
        xpath = self.xpath()
        if( "nzb/file" == xpath ):
            self.nzbFile = NZBFile()
            self.nzbFile.subject = attrs['subject']
        elif( "nzb/file/segments/segment" == xpath ):
            self.nzbSegment = NZBSegment()
            self.nzbSegment.number = int(attrs['number'])
            self.nzbSegment.size = int(attrs['bytes'])
            self.nzbFile.size += self.nzbSegment.size
    def endElement(self,tag):
        xpath = self.xpath()
        if( "nzb/file" == xpath ):
            self.nzbFile.orderSegments()
            self.files.append( self.nzbFile )
            self.nzbFile = None
        elif( "nzb/file/segments/segment" == xpath ):
            self.nzbFile.segments.append( self.nzbSegment )
            self.nzbSegment = None
        self.path.pop()
    def characters(self,data):
        xpath = self.xpath()
        if( "nzb/file/groups/group" == xpath ):
            self.nzbFile.group += data
        elif( "nzb/file/segments/segment" == xpath ):
            self.nzbSegment.msgid += data
    def getNzb(self):
        nzb = NZB()
        nzb.files = self.files
        for file in nzb.files:
            nzb.size += file.size
        return nzb

class NZB(object):
    def __init__(self):
        self.files = []           # the files part of this download
        self.size = 0             # bytes total
            
class NZBFile(object):
    def __init__(self):
        self.subject = None       # the subject for posting of this file
        self.realFileName = None  # the real filename of the attachment in this post
        self.group = ""           # the group where the file was posted
        self.segments = []        # the message id's which make up the file
        self.size = 0
    def orderSegments(self):
        "Ensure that this File's segments are ordered correctly."
        segs = [ (el.number,el) for el in self.segments ]
        segs.sort()
        self.segments = [ el[1] for el in segs ]
            
MAX_RETRIES = 3
class NZBSegment(object):
    def __init__(self):
        self.number = None        # the part number of the segment
        self.msgid = ""           # unique message id of this segment
        self.size = 0
        self.retries = 0
        self.data = []
        self.decodedSize = 0
        self.filename = ""
        self.crc = ""
        self.partnum = 0

    def lastTry(self):
        return ( self.retries == MAX_RETRIES )

    def aborted(self):
        return ( self.retries > MAX_RETRIES )
            
def parseString( str ):
    def func(h): saxParseString( str, h )
    return _parse( func )
         
def parse( file ):
    def func(h): saxParse( file, h )
    return _parse( func )
            
def _parse( f ):
    handler = NZBParser()
    try:
        f( handler )
    except (SAXException):
        log.error( "Failed to parse XML." )
        return None
    
    nzb = handler.getNzb()

    return nzb
