import urllib2, mt, os

class Result:
    def __init__(self):
        self.id = 0
        self.name = ""
        self.size = "0K"

class NZBMatrix:
    def __init__(self, username, apikey, save_to):
        self.user = username
        self.api = apikey
        self.save_to = save_to

    def search(self, query, cat):
        query = query.replace(" ", "%20")

        url = "http://api.nzbmatrix.com/v1.1/search.php?search=" + query + "&catid=" + cat + "&username=" + self.user + "&apikey=" + self.api + "&num=50&englishonly=1"

        response = urllib2.urlopen(url)
        data = ""
        while 1:
            d_in = response.read()
            if not d_in:
                break
            data += d_in
        lines = data.split("\n")

        mt.log.debug("NZBMatrix Response:\n" + data)

        results = []
        result = Result()
        for line in lines:
            if ( line == "|" ):
                results.append(result)
                result = Result()
                continue

            args = line.split(":")
            if ( len(args) > 1 ):
                name = args[0]
                value = args[1][:-1]
                if ( name == "NZBID" ):
                    result.id = int(value)
                if ( name == "NZBNAME" ):
                    result.name = value
                if ( name == "SIZE" ):
                    result.size = mt.utils.convert_bytes(value)

        return results

    def download(self, id):
        try:
            url = "http://api.nzbmatrix.com/v1.1/download.php?id=" + str(id) + "&username=" + self.user + "&apikey=" + self.api
            response = urllib2.urlopen(url)
            info = response.info()
            filename = info["Content-Disposition"].split('filename="')[1][:-1]
            filepath = os.path.join(self.save_to, filename)

            data = response.read()
            fout = open(filepath, "wb")
            fout.write(data)
            fout.close()
            return True
        except:
            return False

