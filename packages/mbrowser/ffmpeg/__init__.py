import re, os, subprocess, fcntl, select, threading
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
        cmd = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
        fcntl.fcntl(
            cmd.stderr.fileno(),
            fcntl.F_SETFL,
            fcntl.fcntl(
                cmd.stderr.fileno(),
                fcntl.F_GETFL
            ) | os.O_NONBLOCK,
        )

        duration = None
        header = ""
        progress_regex = re.compile(
            "frame=.*time=([0-9\:\.]+)",
            flags=re.IGNORECASE
        )
        header_received = False

        while True:
            progressline = select.select([cmd.stderr.fileno()], [], [])[0]
            if progressline:
                line = cmd.stderr.read()
                if line == "":
                    if self.status_callback:
                        self.status_callback(self.output_file, 101)
                    break

                progress_match = progress_regex.match(line)
                if progress_match:
                    if not header_received:
                        header_received = True

                        if re.search(
                            ".*command\snot\sfound",
                            header,
                            flags=re.IGNORECASE
                        ):
                            mt.log.error("ffmpeg: Command error")

                        if re.search(
                            "Unknown format",
                            header,
                            flags=re.IGNORECASE
                        ):
                            mt.log.error("ffmpeg: Unknown format")

                        if re.search(
                            "Duration: N\/A",
                            header,
                            flags=re.IGNORECASE | re.MULTILINE
                        ):
                            mt.log.error("ffmpeg: Unreadable file")

                        raw_duration = re.search(
                            "Duration:\s*([0-9\:\.]+),",
                            header
                        )
                        if raw_duration:
                            units = raw_duration.group(1).split(":")
                            duration = (int(units[0]) * 60 * 60 * 1000) + \
                                (int(units[1]) * 60 * 1000) + \
                                int(float(units[2]) * 1000)

                    if duration and self.status_callback:
                        self.status_callback(self.output_file, int((float(progress_match.group(1))*1000)/float(duration)*100.0))

                else:
                    header += line

def convertToFlash(input_file, status_callback, output_file = ""):
    if ( output_file == "" ):
        output_file = input_file.replace(".avi", ".flv")
    t = ffmpegThread(input_file, output_file, status_callback)
    t.start()

def stop():
    global fThread
    if ( fThread != None ): fThread.close(True)






