import re
import _yenc
import string

class yEncDecoder(object):
    yencRegex = re.compile( "^=ybegin " )
    yencStartRegex = re.compile( "^(=ypart|=ybegin) " )
    yencEndRegex = re.compile( "^=yend" )
    nameRegex = re.compile( ".*name=(.*)" )
    startSizeRegex = re.compile( "=ypart begin=(.*) " )
    endSizeRegex = re.compile( ".*end=(.*) " )
    yencTr = ''.join([chr((i + 256 - 42) % 256) for i in range(256)])

    yenc42 = string.join(map(lambda x: chr((x-42) & 255), range(256)), "")
    yenc64 = string.join(map(lambda x: chr((x-64) & 255), range(256)), "")

    @classmethod
    def supports(self,lines):
        for n in xrange(0,min(100,len(lines))): #only search first 100 lines and give up
            line = lines[n]
            if self.yencRegex.match(line):
                return line;
        return False

    def getRealFilename(self,lines):
        match = self.nameRegex.match(self.supports(lines))
        if match: return match.group(1)
        else: return None

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

    def decode(self,lines):
        data = []
        isData = False
        for line in lines:
            if self.yencEndRegex.match(line): break
            if self.yencStartRegex.match(line):
                isData = True
            elif isData: data.append(line)

        data = "".join(data)

        for i in (0, 9, 10, 13, 27, 32, 46, 61):
            j = '=%c' % (i + 64)
            data = data.replace(j, chr(i))
            
        return data.translate( self.yencTr )

    def hella_decode(self, lines):
        buffer = []

        lines = self.stripArticleData(lines)

        inContent = False
        for line in lines:
            if line[:2] == '..':
                line = line[1:]
            if line[-2:] == "\r\n":
                line = line[:-2]
            elif line[-1:] in "\r\n":
                line = line[:-1]

            if (line[:7] == '=ybegin') or (line[:6] == '=ypart'):
                inContent = True
                continue
            elif line[:5] == '=yend':
                break
            if ( inContent ): buffer.append(line)

        data = ''.join(buffer)
        decoded_data = _yenc.decode_string(data)[0]
        return decoded_data

    def testDecode(self, lines):
        i = 0
        start_line = -1
        end_line = -1

        #print "Line size before stripping:" + str(len(lines))
        self.stripArticleData(lines)
        #print "Line size after stripping:" + str(len(lines))

        for line in lines:
            if line[:2] == '..':
                line = line[1:]
            if line[-2:] == "\r\n":
                line = line[:-2]
            elif line[-1:] in "\r\n":
                line = line[:-1]

            if ( line[:6] == "=ypart" ):
                start_line = i+1
            if ( line[:5] == "=yend"):
                end_line = i

            i += 1

        if ( start_line > -1 ) and ( end_line > -1 ):
            data = "".join(lines[start_line:end_line])     
            decoded_data, size, num = _yenc.decode_string(data)
            #print decoded_data
            return decoded_data
        return None

    def yenc_decode(self, lines):
        # find body
        x = 0
        print "Line size before stripping:" + str(len(lines))
        self.stripArticleData(lines)
        print "Line size after stripping:" + str(len(lines))

        while (x < len(lines)):
            line = lines[x]
            if not line:
                return None
            if line[:7] == "=ybegin":
                break
            x += 1
        # extract data
        buffer = []
        while (x < len(lines)):
            line = lines[x]
            if not line or line[:5] == "=yend":
                break
            if line[-2:] == "\r\n":
                line = line[:-2]
            elif line[-1:] in "\r\n":
                line = line[:-1]
            data = string.split(line, "=")
            buffer.append(string.translate(data[0], self.yenc42))
            for data in data[1:]:
                data = string.translate(data, self.yenc42)
                buffer.append(string.translate(data[0], self.yenc64))
                buffer.append(data[1:])
            x+=1
        return "".join(buffer)  
    
    MIME_HEADER_RE = re.compile('^(\w|-)+: .*$')
    def stripArticleData(self, articleData):
        """ Rip off leading/trailing whitespace (and EOM char) from the articleData list """
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
            
