import gzip, urllib, urllib2, os
from StringIO import StringIO

class Binsearch():

    class Result:
        def __init__(self):
            self.id = 0
            self.name = ""
            self.size = "0K"
    
    def __init__(self, save_to):
        self.save_to = save_to

    def openURL(self, url, data = None):
        request = urllib2.Request(url, data)
        request.add_header('Accept-encoding', 'gzip')
        response = urllib2.urlopen(request)
        
        data = ""
        if response.info().get('Content-Encoding') == 'gzip':
            buf = StringIO( response.read())
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()    
        else:
            data = response.read()
        
        return data

    def search(self, query):
        query_string = urllib.urlencode({"q": query, "max": "50"})        
        url = "http://binsearch.info/?" + query_string
        data = self.openURL(url)

        result_list = []
        data = data.split("<td><input type=\"checkbox\" name=\"")

        if ( len(data) > 3 ):
            data = data[2:-1]
            for raw_nzb in data:
                raw_nzb = raw_nzb.split("\" ><td><span class=\"s\">")
                
                result = self.Result()
                result.id = int(raw_nzb[0])
                result.name = raw_nzb[1].split("</span>")[0]

                # try for size
                a = raw_nzb[1].split("size: ")
                if ( len(a) > 1 ):
                    result.size = a[1].split(", parts")[0].replace("&nbsp;", " ")

                result_list.append(result)

        return result_list

    def download(self, id, filename):
        url = "http://binsearch.info/fcgi/nzb.fcgi"
        post_data = str(id) + "=on&action=nzb"    
        data = self.openURL(url, post_data)

        f = open(os.path.join(self.save_to, filename), "w")
        f.write(data)
        f.close()
        return True

