from xml.sax import parse as saxParse
from xml.sax import parseString as saxParseString
from xml.sax import handler,SAXException,SAXParseException
from xml.sax.xmlreader import XMLReader
from xml.sax.expatreader import ExpatParser

MAX_RETRIES = 0                   # maximum retries of a segment before giving up.

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


class NZBSegment(object):
    def __init__(self):
        # this info is gathered from the NZB file itself.
        self.number = None
        self.msgid = ""
        self.size = 0

        # these are related to the actual download of the segment.
        self.retries = 0
        self.data = []

        # values obtained after the article is decoded.
        self.decoded_data = ""
        self.decoded_size = 0
        self.decoded_filename = ""
        self.decoded_crc = ""
        self.decoded_number = 0

    def lastTry(self):
        return ( self.retries == (MAX_RETRIES-1) )

    def aborted(self):
        return ( self.retries >= MAX_RETRIES )

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
            
def parseString( str ):
    def func(h): saxParseString( str, h )
    return _parse( func )
         
def parse( file ):
    h = NZBParser()
    p = ExpatParser()
    p.setContentHandler(h)
    p.setFeature(handler.feature_external_ges, False)
    p.parse(file)
    nzb = h.getNzb()
    return nzb
    
    #def func(h): saxParse( file, h )
    #return _parse( func )
            
def _parse( f ):
    handler = NZBParser()
    #try:
    f( handler )
    #except (SAXParseException):
    #    pass
    #except (SAXException):
    #    return None
    
    nzb = handler.getNzb()

    return nzb
