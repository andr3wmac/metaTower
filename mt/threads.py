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
pool_pid = 0

def stopAll():
    global pool, pool_pid
    if ( pool_pid != os.getpid() ): return

    for t in pool:
        try:
            t.stop()
        except:
            pass

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

    def _checkPool(self):
        global pool, pool_pid
        pid = os.getpid()
        if ( pool_pid != pid ):
            pool = []
            pool_pid = pid

    def start(self):
        try:
            self._checkPool()
            pool.append(self)
            self.running = True
            threading.Thread.start(self)
        except:
            self.running = False

    def stop(self):
        self.running = False

class Process(Thread):
    class ProcessShell(multiprocessing.Process):
        def __init__(self, target, args, kwargs, conn):
            multiprocessing.Process.__init__(self)
            self.connection = conn
            self.target = target
            self.args = args
            self.kwargs = kwargs

        def run(self):
            if ( inspect.isfunction(self.target) ):
                self.target(*self.args, **self.kwargs)            

            # if we have a class, create it and allow functions to be
            # called using the execute() function in the parent class.
            if ( inspect.isclass(self.target) ):
                # create and start the object.
                self.obj = self.target(*self.args, **self.kwargs)
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

            # this will try to kill the pool in case any threads were
            # created by this process
            stopAll()

    def __init__(self, target, *args, **kwargs):
        Thread.__init__(self)
        parent_conn, child_conn = multiprocessing.Pipe()
        self.process = self.ProcessShell(target, args, kwargs, child_conn)
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
