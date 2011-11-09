import re, _yenc, string, os, time
import mtCore as mt
from threading import Thread

class ArticleDecoder(Thread):
    def __init__(self, nextSeg, save_to, path, onFinish = None, onSuccess = None, onFail = None):
        Thread.__init__(self)
        self.daemon = True

        self.nextSeg = nextSeg
        self.save_to = save_to
        self.onFinish = onFinish
        self.onSuccess = onSuccess
        self.onFail = onFail
        self.running = True

        self.path = path

    def run(self):
        while ( self.running ):
            try:
                seg = self.nextSeg()
                if ( seg == None ): 
                    time.sleep(1)                
                    continue
                if ( seg == -1 ):
                    # this means we're finished here.
                    self.assembleSegments()
                    self.running = False
                    break
                self.decodeSegment(seg)
            except Exception as inst:
                mt.log.error("ArticleDecoder running error: " + str(inst.args))
                self.running = False
        if ( self.onFinish ): self.onFinish()

    def assembleSegments(self):
        mt.log.debug("Assembling..")
        decoder = yEncDecoder()

        # generate list of files.
        file_index = {}
        for cache_file in os.listdir(self.path):
            file_name = cache_file[:-4]
            if ( not file_index.has_key(file_name) ):
                file_index[file_name] = []
            file_index[file_name].append(cache_file)

        # check if the save folder exists
        if ( not os.path.isdir(self.save_to) ): os.mkdir(self.save_to)
        for file_name in file_index:
            try:
                file = open(os.path.join(self.save_to, file_name), "wb")
                file_index[file_name].sort()
                segments = file_index[file_name]
                mt.log.debug("Assembling File: " + file_name + " Total Segments: " + str(len(segments)))

                total_data = 0
                for seg in segments:
                    seg_f = open(os.path.join(self.path, seg), "rb")
                    seg_data = seg_f.read()
                    seg_f.close()

                    seg_size = len(seg_data)
                    total_data += len(seg_data)
                    
                    if ( seg_data ): file.write(seg_data)
                    os.remove(os.path.join(self.path, seg))

                file.close()
                mt.log.debug("Assembled file: " + file_name + " Size: " + str(total_data) + " byte(s)")
            except Exception as inst:
                mt.log.error("File assembly error: " + str(inst.args))

    def decodeSegment(self, seg):
        decoder = yEncDecoder()
        try:
            if ( decoder.decode(seg) ):
                file_path = os.path.join(self.path, seg.filename + "." + str("%03d" % (seg.partnum,)))
                cache_file = open(file_path, "wb")
                cache_file.write(seg.decodedData)
                cache_file.close()

                # memory leaks really bad without this.
                del seg.data[:]
                seg.decodedData = ""

                if ( self.onSuccess ): self.onSuccess(seg)
            else:
                if ( self.onFail ): self.onFail(seg)

        except Exception as inst:
            mt.log.error("ArticleDecoder decode segment(" + seg.msgid + ") error: " + str(inst.args))
            if ( self.onFail ): self.onFail(seg)

        finally:
            del seg.data[:]

class yEncDecoder(object):
    def getFilename(self,lines):
        for line in lines:
            if ( line[:7] == "=ybegin" ):
                args = line.split(" ")
                fname = args[len(args)-1].split("=")[1]
                if fname[-2:] == "\r\n":
                    fname = fname[:-2]
                elif fname[-1:] in "\r\n":
                    fname = fname[:-1]
                return fname
        return None

    def getPartNum(self, lines):
        for line in lines:
            if ( line[:7] == "=ybegin" ):
                args = line.split(" ")
                return int(args[1].split("=")[1])

    def getPartBegin(self,lines):
        for line in lines:
            if ( line[:6] == "=ypart" ):
                args = line.split(" ")
                return args[1].split("=")[1]
        return None

    def getPartEnd(self,lines):
        for line in lines:
            if ( line[:6] == "=ypart" ):
                args = line.split(" ")
                return args[2].split("=")[1]
        return None

    def decode(self, seg):
        ignoreErrors = seg.lastTry()
        buffer = []
        #print seg.data[0]
        #print seg.data[1]
        #lines = self.stripArticleData(seg.data)

        inBody = False
        endFound = False
        for line in seg.data:
            #if line[:2] == '..':
            #    line = line[1:]
            #if line[-2:] == "\r\n":
            #    line = line[:-2]
            #elif line[-1:] in "\r\n":
            #    line = line[:-1]

            if (line[:7] == '=ybegin'):
                args = line.split(" ")
                for arg in args:
                    if ( arg.startswith("name=") ):
                        seg.filename = arg.split("=")[1]
                    if ( arg.startswith("part=") ):
                        seg.partnum = int(arg.split("=")[1])

            elif (line[:6] == '=ypart'):
                inBody = True
                continue

            elif (line[:5] == '=yend'):
                args = line.split(" ")
                for arg in args:
                    if ( arg.startswith("pcrc32=") or arg.startswith("crc32=") ):
                        seg.crc = arg.split("=")[1]

                endFound = True
                break
            if ( inBody ): buffer.append(line)

        # no ending found, article must have been cut off in transmit.
        if ( not endFound ) and ( not ignoreErrors ): 
            mt.log.error("Article decode error: =yend not found.")           
            return False

        # join the data together and decode it.
        data = ''.join(buffer)
        decoded_data, crc, something = _yenc.decode_string(data)
        
        # if the article has failed multiple times we'll ignore errors and take
        # whatever we can get from it.
        if ( not ignoreErrors ):
            # If a CRC was included, check it.
            #if ( seg.crc != "" ):
            #    crc = '%08X' % ((crc ^ -1) & 2**32L - 1)
            #    if ( seg.crc.upper() != crc ):
            #        print "CRC check failed."
            #        return False

            # check partnum
            if ( seg.partnum != seg.number ):
                mt.log.error("Part number does not match: " + seg.msgid)
                if ( self.onFail ): self.onFail(seg)
                return False

            # ensure we decoded a filename.
            if ( seg.filename == "" ):
                print "No filename found."
                return False
        else:
            if ( seg.partnum != seg.number ): seg.partnum = seg.number

        seg.decodedSize = len(decoded_data)
        seg.decodedData = decoded_data
        return True
    
    MIME_HEADER_RE = re.compile('^(\w|-)+: .*$')
    def stripArticleData(self, articleData):
        try:
            # Rip off the leading whitespace
            while articleData[0] == '' or self.MIME_HEADER_RE.match(articleData[0]):
                articleData.pop(0)

            # and trailing
            while articleData[-1] == '':
                articleData.pop(-1)

            # Remove the EOM char
            if articleData[-1] == '..' or articleData[-1] == '.':
                articleData.pop(-1)
                
                # and trailing again
                while articleData[-1] == '':
                    articleData.pop(-1)
                
        except IndexError:
            pass

        return articleData
            
