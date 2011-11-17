import urllib2, sys, threading, time, os, mtMisc

class PackageDownloader(threading.Thread):
    class fileDownload():
        def __init__(self, url, save_to):
            self.url = url
            self.save_to = save_to
            self.response = urllib2.urlopen(url)
            self.size = int(self.response.info().getheader('Content-Length').strip())
            self.completed = 0
          
    def __init__(self, status_hook, install_done_hook, update_done_hook):
        threading.Thread.__init__(self)
        self.daemon = True
        self.file_queue = []
        self.status_hook = status_hook
        self.install_done_hook = install_done_hook
        self.update_done_hook = update_done_hook
        self.status_time = 0
        self.running = False
        self.package = None
        self.installing = False

    def add(self, url, save_to):
        f = self.fileDownload(url, save_to)
        self.file_queue.append(f)

    def updatePackage(self, package):
        if ( package.source_url != "" ):
            for f in package.install_files:
                url = package.source_url + package.id + "/" + f
                path = os.path.join("packages", package.id, f)
                self.add(url, path)
            self.package = package
            self.installing = False
            self.start()

    def installPackage(self, package):
        if ( package.source_url != "" ):
            for f in package.install_files:
                url = package.source_url + package.id + "/" + f
                path = os.path.join("packages", package.id, f)
                self.add(url, path)
            self.package = package
            self.installing = True
            self.start()

    def updateStatus(self):
        if ( time.time() - self.status_time > 0.25 ):
            total_queued = 0
            total_completed = 0
            for f in self.file_queue:
                total_queued += f.size
                total_completed += f.completed

            if ( self.status_hook ):
                self.status_hook(self.package, total_queued, total_completed)
            self.status_time = time.time()
        
    def run(self):
        chunk_size = 8192
        for f in self.file_queue:
            bytes_so_far = 0
            path = f.save_to.replace(os.path.basename(f.save_to), "")
            mtMisc.mkdir(path)
            fout = open(f.save_to, "wb")
            while 1:
                chunk = f.response.read(chunk_size)
                f.completed += len(chunk)
                fout.write(chunk)

                if not chunk:
                    break

                self.updateStatus()
            fout.close()

        if ( self.installing ):
            if ( self.install_done_hook ): self.install_done_hook(self.package)
        else:
            if ( self.update_done_hook ): self.update_done_hook(self.package)
