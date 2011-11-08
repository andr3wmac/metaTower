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
            # split up the data, process it and write it disk.
            data = seg.data.split("\r\n")
            filename = decoder.getFilename(data)
            partnum = decoder.getPartNum(data)
            decoded_data = decoder.decode(data, seg.lastTry())
            seg.data = "" # this prevents a massive memory leak that took me 45 minutes to find.

            # check if the partnum matches.
            if ( partnum != seg.number ):
                mt.log.error("Part number does not match: " + seg.msgid)
                if ( self.onFail ): self.onFail(seg)
                return

            # if we have all we need write to cache.
            if ( filename ) and ( partnum ) and ( decoded_data ):
                file_path = os.path.join(self.path, filename + "." + str("%03d" % (partnum,)))
                mt.log.debug("Writing segment: " + file_path + " Size: " + str(len(decoded_data)))
                cache_file = open(file_path, "wb")
                cache_file.write(decoded_data)
                cache_file.close()
                if ( self.onSuccess ): self.onSuccess(seg)
            else:
                mt.log.debug("Segment decode failed: " + seg)
                if ( self.onFail ): self.onFail(seg)

        except Exception as inst:
            mt.log.error("ArticleDecoder decode segment(" + seg.msgid + ") error: " + str(inst.args))
            if ( self.onFail ): self.onFail(seg)


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

    def decode(self, lines, ignoreErrors = False):
        buffer = []
        lines = self.stripArticleData(lines)

        inBody = False
        endFound = False
        for line in lines:
            if line[:2] == '..':
                line = line[1:]
            if line[-2:] == "\r\n":
                line = line[:-2]
            elif line[-1:] in "\r\n":
                line = line[:-1]

            if (line[:7] == '=ybegin') or (line[:6] == '=ypart'):
                inBody = True
                continue
            elif line[:5] == '=yend':
                endFound = True
                break
            if ( inBody ): buffer.append(line)

        if ( not endFound ) and ( not ignoreErrors ): 
            mt.log.error("Article decode error: =yend not found.")           
            return None

        data = ''.join(buffer)
        decoded_data = _yenc.decode_string(data)[0]
        return decoded_data
    
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
            
