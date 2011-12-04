import pexpect, re, threading, os

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

        if ( os.path.isfile(output_file) ):
            os.remove(output_file)
        
    def run(self):
        global fThread

        cmd = '/usr/bin/ffmpeg -i ' + self.input_file.replace(" ", "\\ ") + ' -ac 2 -ab 96k -ar 44100 -b 345k -s 640x360 ' + self.output_file.replace(" ", "\\ ")
        fThread = pexpect.spawn(cmd)
        fThread.expect("  Duration: (.+), start:")
        duration = self.hmsToSeconds(fThread.match.group(1)[11:-11])

        cpl = fThread.compile_pattern_list([
            pexpect.EOF,
            "time=(.+) bitrate="
        ])

        percent_complete = 0
        while True:
            i = fThread.expect_list(cpl, timeout=None)
            if i == 0: # EOF
                if ( self.status_callback ): self.status_callback(self.output_file, 101)
                break
            elif i == 1:
                t = fThread.match.group(1)
                percent = int((float(t) / duration) * 100)
                if ( percent != percent_complete ):
                    percent_complete = percent
                    if ( self.status_callback ): self.status_callback(self.output_file, percent)
                fThread.close
            elif i == 2:
                #unknown_line = thread.match.group(0)
                #print unknown_line
                pass

def convertToFlash(input_file, status_callback, output_file = ""):
    if ( output_file == "" ):
        output_file = input_file.replace(".avi", ".flv")
    t = ffmpegThread(input_file, output_file, status_callback)
    t.start()

def stop():
    global fThread
    if ( fThread != None ): fThread.close(True)






