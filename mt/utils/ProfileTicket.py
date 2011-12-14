import time, mt

class ProfileTicket:
    def __init__(self, args = []):
        self.start_time = time.time()
        self.end_time = 0
        self.start_args = args

    def end(self, args = []):
        src = mt.utils.getSource()
        self.end_time = time.time()
        args = self.start_args + args
        mt.log.debug("Profile of " + src + " ended in " + str(self.end_time-self.start_time) + " ARGS:" + str(args))
