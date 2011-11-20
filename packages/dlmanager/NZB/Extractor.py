from os import system,path
import re,shutil

RAR = "/usr/bin/unrar"

class rarExtractor(object):
    def __init__(self):
        self.isRarRunning = False
    @classmethod
    def supports(cls,firstFileName):
        # cheezy hack, i realy wanted to use mime magic
        return firstFileName.endswith( ".rar" )
    def extract(self,file):
        global RAR
        if not self.isRarRunning:
            self.isRarRunning = True
            dir = path.dirname( file )
            f = path.basename( file )
            system( "cd '%s' && %s x '%s' &" % (dir,RAR,f) )

CATREGEX = re.compile( r'(.*)\.\d+$' )

class catExtractor(object):
    def __init__(self):
        self.lastBasename = None
        self.file = None
        pass
    @classmethod
    def supports(cls,firstFileName):
        global CATREGEX
        return CATREGEX.match( firstFileName )
    def extract(self,file):
        global CATREGEX
        match = CATREGEX.match(file)
        basename = match.group(1) if match else file
        
        if not lastBasename == basename:
            if self.file : close( self.file )
            self.file = open( basename, "w" )
            self.lastBasename = basename
        
        thisFile = open( file, "r" )
            
        shutil.copyfile( thisFile, self.file )