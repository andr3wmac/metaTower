import threading, time

pool = []

class Thread(threading.Thread):
    def __init__(self, tick_interval = -1, *args, **kwargs):
        threading.Thread.__init__(self)
        self.running = False     
        self.tick_interval = tick_interval
        self._last_ticktime = 0
        self._tickcount = 0
        self.init(*args, **kwargs)

    def init(self):
        self.running = False

    def tick(self):
        self._tickcount += 1
        print "Tick: " + str(self._tickcount)

    def sleep(self, secs):
        start_time = time.time()
        while (time.time() < (start_time + secs)) and self.running:
            time.sleep(0.1)

    def run(self):
        while self.running:
            if ( self.tick_interval >= 0 ):
                t = time.time()
                if ( t - self._last_ticktime >= self.tick_interval ):
                    self.tick()
                    self._last_ticktime = t
            time.sleep(0.1)

    def start(self):    
        try:
            global pool
            pool.append(self)
            self.running = True
            threading.Thread.start(self)
        except:
            self.running = False

    def stop(self):
        self.running = False

def stopAll():
    global pool
    for t in pool:
        t.stop()
