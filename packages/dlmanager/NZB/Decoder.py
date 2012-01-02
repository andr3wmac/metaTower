import re, string, os, time, mt
from zlib import crc32

yenc_found = False
try:
    import _yenc
    yenc_found = True
except:
    pass

class ArticleDecoder(mt.threads.Thread):
    def __init__(self, nextSeg, save_to, path, onFinish = None, onSuccess = None, onFail = None, onAssemblyPercent = None):
        mt.threads.Thread.__init__(self)
        self.daemon = True
        self.decoder = SegmentDecoder()

        self.nextSeg = nextSeg
        self.save_to = save_to
        self.onFinish = onFinish
        self.onSuccess = onSuccess
        self.onAssemblyPercent = onAssemblyPercent
        self.onFail = onFail
        self.path = path

    def run(self):
        while ( self.running ):
            try:
                seg = self.nextSeg()
                if ( seg == None ): 
                    self.sleep(0.1)                
                    continue

                if ( seg == -1 ):
                    # this means we're finished here.
                    if ( self.onAssemblyPercent ): self.onAssemblyPercent(0)
                    self.assembleSegments()
                    if ( self.onAssemblyPercent ): self.onAssemblyPercent(100)
                    self.running = False
                    break

                self.decodeSegment(seg)

            except Exception as inst:
                mt.log.error("ArticleDecoder running error: " + str(inst.args))
                self.stop()

        if ( self.onFinish ): self.onFinish()

    def assembleSegments(self):
        if ( not self.running ): return
        mt.log.debug("Assembling..")

        # generate list of files.
        file_index = {}
        for cache_file in os.listdir(self.path):
            file_name = cache_file[:-4]
            if ( not file_index.has_key(file_name) ):
                file_index[file_name] = []
            file_index[file_name].append(cache_file)

        # check if the save folder exists
        if ( not os.path.isdir(self.save_to) ): os.mkdir(self.save_to)
        file_count = len(file_index)
        files_complete = 0
        for file_name in file_index:
            try:
                file = open(os.path.join(self.save_to, file_name), "wb")
                file_index[file_name].sort()
                segments = file_index[file_name]
                mt.log.debug("Assembling File: " + file_name + " Total Segments: " + str(len(segments)))
                for seg in segments:
                    seg_f = open(os.path.join(self.path, seg), "rb")
                    seg_data = seg_f.read()
                    seg_f.close()
                    
                    if ( seg_data ): file.write(seg_data)
                    os.remove(os.path.join(self.path, seg))

                file.close()
                mt.log.debug("Assembled file: " + file_name + ".")

            except Exception as inst:
                mt.log.error("File assembly error: " + str(inst.args))
            
            # report assembly completion status
            if ( self.onAssemblyPercent ):
                files_complete += 1
                percent = int((float(files_complete)/float(file_count))*100.0)
                self.onAssemblyPercent(percent)

    def decodeSegment(self, seg):
        try:
            if ( self.decoder.yenc_decode(seg) ):
                file_path = os.path.join(self.path, seg.decoded_filename + "." + str("%03d" % (seg.decoded_number,)))
                cache_file = open(file_path, "wb")
                cache_file.write(seg.decoded_data)
                cache_file.close()

                # memory leaks really bad without this.
                del seg.data[:]
                seg.decoded_data = ""

                if ( self.onSuccess ): self.onSuccess(seg)
            else:
                if ( self.onFail ): self.onFail(seg)

        except Exception as inst:
            mt.log.error("ArticleDecoder decode segment(" + seg.msgid + ") error: " + str(inst.args))
            if ( self.onFail ): self.onFail(seg)

        finally:
            del seg.data[:]


class SegmentDecoder(object):
    def __init__(self):
        self.YDEC_TRANS = ''.join([chr((i + 256 - 42) % 256) for i in range(256)])

    def yenc_decode(self, seg):
        ignore_errors = seg.lastTry()
        buffer = []
        in_body = False
        end_found = False

        for line in seg.data:
            if (line[:7] == '=ybegin'):
                args = line.split(" ")
                for arg in args:
                    if ( arg.startswith("name=") ):
                        seg.decoded_filename = line.split("=")[-1]
                    if ( arg.startswith("part=") ):
                        seg.decoded_number = int(arg.split("=")[1])

            elif (line[:6] == '=ypart'):
                in_body = True
                continue

            elif (line[:5] == '=yend'):
                args = line.split(" ")
                for arg in args:
                    if ( arg.startswith("pcrc32=") or arg.startswith("crc32=") ):
                        c = arg.split("=")[1]
                        seg.decoded_crc = '0' * (8 - len(c)) + c

                end_found = True
                break
            if ( in_body ): buffer.append(line)

        # no ending found, article must have been cut off in transmit.
        if ( not end_found ) and ( not ignore_errors ): 
            mt.log.debug("Article decode error: =yend not found.")           
            return False

        # join the data together and decode it.
        data = ''.join(buffer)
        crc = ""
        if ( yenc_found ):
            decoded_data, _yenc_crc, something = _yenc.decode_string(data)
            crc = '%08X' % ((_yenc_crc ^ -1) & 2**32L - 1)
        else:
            # stolen from hellanzb.
            for i in (0, 9, 10, 13, 27, 32, 46, 61):
                j = '=%c' % (i + 64)
                data = data.replace(j, chr(i))
            decoded_data = data.translate(self.YDEC_TRANS)
            crc = '%08X' % (crc32(decoded_data) & 2**32L - 1)
        
        # if the article has failed multiple times we'll ignore errors and take
        # whatever we can get from it.
        if ( not ignore_errors ):
            # If a CRC was included, check it.
            if ( seg.decoded_crc != "" ) and ( crc != "" ):
                if ( seg.decoded_crc.upper() != crc ):
                    mt.log.debug("CRC does not match. A: " + seg.decoded_crc.upper() + " B: " + crc)
                    return False

            # check partnum
            if ( seg.decoded_number != seg.number ):
                mt.log.debug("Part number does not match: " + seg.msgid)
                return False

            # ensure we decoded a filename.
            if ( seg.decoded_filename == "" ):
                mt.log.debug(seg.msgid + " does not have a filename.")
                return False
        else:
            if ( seg.decoded_number != seg.number ): seg.decoded_number = seg.number

        seg.decoded_size = len(decoded_data)
        seg.decoded_data = decoded_data
        return True
            
