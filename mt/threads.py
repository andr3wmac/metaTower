"""
 * metaTower v0.4.0
 * http://www.metatower.com
 *
 * Copyright 2011, Andrew MacIntyre
 * http://www.andrewmac.ca
 * Licensed under GPL v3.
 * See license.txt 
 *  or http://www.metatower.com/license.txt
"""

import os, imp, multiprocessing, threading, inspect, time

pool = []

class Thread(threading.Thread):
    def __init__(self, tick_interval = -1):
        threading.Thread.__init__(self)
        self.running = False     
        self.tick_interval = tick_interval
        self._last_ticktime = 0
        self._tickcount = 0

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

class Process(Thread):
    class ProcessShell(multiprocessing.Process):
        def __init__(self, p_class, args, kwargs, conn):
            multiprocessing.Process.__init__(self)
            self.connection = conn
            self.p_class = p_class
            self.args = args
            self.kwargs = kwargs

        def run(self):
            if ( not inspect.isclass(self.p_class) ): return None

            # create and start the object.
            self.obj = self.p_class(*self.args, **self.kwargs)
            if hasattr(self.obj, "start"): self.obj.start()

            data = self.connection.recv()
            while data != None:
                function_name = data[0]
                function_args = data[1:]

                result = None
                if hasattr(self.obj, function_name):
                    _func = getattr(self.obj, function_name)
                    result = _func(*function_args)

                self.connection.send(result)
                data = self.connection.recv()

            # stop if available.
            if hasattr(self.obj, "stop"): self.obj.stop()
            del self.obj

    def __init__(self, p_class, *args, **kwargs):
        Thread.__init__(self)
        parent_conn, child_conn = multiprocessing.Pipe()
        self.process = self.ProcessShell(p_class, args, kwargs, child_conn)
        self.connection = parent_conn
        self.connection_lock = threading.Lock()

    def run(self):
        self.process.start()
        while self.running:
            self.sleep(0.1)
        self.connection.send(None)
        self.process.join()

    def execute(self, *args):
        result = None
        self.connection_lock.acquire()
        try:
            self.connection.send(args)
            result = self.connection.recv()
        finally:
            self.connection_lock.release()
        return result

def stopAll():
    global pool
    for t in pool:
        t.stop()
