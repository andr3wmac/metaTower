import os, mt

converting = False
statusCallback = None
input_file = ""
output_file = ""
execute_thread = None
duration = None

def hmsToSeconds(h, m, s):
    #h, m, s = string.split(":")
    #print string + " h: " + str(len(h)) + " s: " + str(len(s))
    total = float(s) + (float(m)*60.0) + (float(h)*3600.0)
    return total

def onEOF():
    global statusCallback, output_file
    if ( statusCallback ): statusCallback(output_file, 101)

def onMatch(index, matches):
    global statusCallback, output_file, duration

    # duration
    if ( index == 0 ):
        args = matches[0].split(":")
        if ( len(args) == 1 ):
            duration = float(args[0])
        if ( len(args) == 3 ):
            duration = hmsToSeconds(args[0], args[1], args[2])

    # time        
    if ( index == 1 ):
        args = matches[0].split(":")
        if ( len(args) == 1 ):
            time = float(args[0])
        if ( len(args) == 3 ):
            time = hmsToSeconds(args[0], args[1], args[2])

        if ( duration != None ):
            if ( statusCallback ): statusCallback(output_file, int((time/duration)*100.0))

def convertToFlash(f_in, s_callback, f_out = ""):
    global statusCallback, converting, output_file, input_file, execute_thread
    if ( converting ): return

    # if no output file specified we assume its the same name.
    if ( f_out == "" ):
        basename, ext = os.path.splitext(f_in)
        f_out = f_in.replace(ext, ".flv")

    # store these for later
    input_file = f_in
    output_file = f_out
    statusCallback = s_callback

    # grab our config settings.
    cmd = [mt.config["mbrowser/ffmpeg/" + os.name], "-i", input_file]
    cmd += ["-ac", mt.config["mbrowser/ffmpeg/audio/channels"]]
    cmd += ["-ab", mt.config["mbrowser/ffmpeg/audio/bitrate"]]
    cmd += ["-ar", mt.config["mbrowser/ffmpeg/audio/freq"]]
    cmd += ["-b", mt.config["mbrowser/ffmpeg/video/bitrate"]]
    cmd += ["-s", mt.config["mbrowser/ffmpeg/video/size"]]
    cmd += [output_file]

    # execute command. this will work on windows or unix.
    execute_thread = mt.utils.execute_async(cmd, 
                        ["Duration:\s*([0-9\:\.]+),", "frame=.*time=([0-9\:\.]+)"], 
                        eofCallback = onEOF, 
                        matchCallback = onMatch)

def stop():
    global execute_thread
    if ( execute_thread ):
        execute_thread.stop()    
