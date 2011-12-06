import pexpect, re, threading, os
import mtCore as mt

fThread = None
class ffmpegThread(threading.Thread):
    def hmsToSeconds(self, string):
        h, m, s = string.split(":")
        #print string + " h: " + str(len(h)) + " s: " + str(len(s))
        total = float(s) + (float(m)*60.0) + (float(h)*3600.0)
        return total
    
    def __init__(self, input_file, output_file, status_callback):
        threading.Thread.__init__(self)
        self.daemon = True
        self.input_file = input_file
        self.output_file = output_file
        self.status_callback = status_callback

        self.cmd = mt.config["mbrowser/ffmpeg/" + os.name]
        self.cmd_args = " -ac " + mt.config["mbrowser/ffmpeg/audio/channels"]
        self.cmd_args += " -ab " + mt.config["mbrowser/ffmpeg/audio/bitrate"]
        self.cmd_args += " -ar " + mt.config["mbrowser/ffmpeg/audio/freq"]
        self.cmd_args += " -b " + mt.config["mbrowser/ffmpeg/video/bitrate"]
        self.cmd_args += " -s " + mt.config["mbrowser/ffmpeg/video/size"]

        if ( os.path.isfile(output_file) ):
            os.remove(output_file)
        
    def run(self):
        global fThread
        
        cmd = self.cmd + " -i " + self.input_file.replace(" ", "\\ ") + self.cmd_args + " " + self.output_file.replace(" ", "\\ ")
        mt.log.info("Executing Command: " + cmd)

        fThread = pexpect.spawn(cmd)

        cpl = fThread.compile_pattern_list([
            pexpect.EOF,
            "  Duration: (.+), start:",
            "time=(.+) bitrate="
        ])

        duration = 0
        percent_complete = 0
        while True:
            i = fThread.expect_list(cpl, timeout=None)
            if i == 0: # EOF
                if ( self.status_callback ): self.status_callback(self.output_file, 101)
                break
            elif i == 1:
                duration = self.hmsToSeconds(fThread.match.group(1)[11:-11])
                fThread.close
            elif i == 2:
                t = fThread.match.group(1)
                percent = int((float(t) / duration) * 100)
                if ( percent != percent_complete ):
                    percent_complete = percent
                    if ( self.status_callback ): self.status_callback(self.output_file, percent)
                fThread.close

def convertToFlash(input_file, status_callback, output_file = ""):
    if ( output_file == "" ):
        output_file = input_file.replace(".avi", ".flv")
    t = ffmpegThread(input_file, output_file, status_callback)
    t.start()

def stop():
    global fThread
    if ( fThread != None ): fThread.close(True)






