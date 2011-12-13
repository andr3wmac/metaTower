import mt, os, re

def getLastLine(text):
    args = text.splitlines()
    for x in range(len(args)-1, -1, -1):
        if ( args[x] != "" ): return args[x]

def getRARFiles(path):
    result = []
    folders = []
    if ( not os.path.isdir(path) ): return False

    for f in os.listdir(path):
        ff = os.path.join(path, f)
        if f.lower().endswith(".rar"):
            result.append(ff)
            continue            

        if ( os.path.isdir(ff) ): folders.append(ff)

    for f in folders: result += getRARFiles(f)
    return result

def unrarFolder(path):
    result = False
    extract_files = {}
    rar_files = getRARFiles(path)

    # Generate a list of files to be extracted.
    for rar_file in rar_files:
        rar_file = rar_file.replace(" ", "\ ").replace("(", "\(").replace(")", "\)")

        rar_flist = mt.utils.execute("/usr/bin/unrar lb " + rar_file).splitlines()
        for f in rar_flist:
            mt.log.debug("FROM:" + rar_file + " : " + f)
            if ( f != "" ) and ( not extract_files.has_key(f) ):
                extract_files[f] = rar_file

    # Narrow that list down to just the rar files to be extracted.
    rar_files = mt.utils.removeDuplicates(extract_files.values())

    # Now we actually extract them, only the last result will be shown.
    for rar_file in rar_files:
        mt.log.info("Extracting RAR file: " + rar_file)
        #f = rar_file.replace(" ", "\ ").replace("(", "\(").replace(")", "\)")
        output = mt.utils.execute("/usr/bin/unrar e -o+ -ts0 " + rar_file + " " + mt.config["dlmanager/nzb/save_to"])
        result = getLastLine(output)

    return result

def getPAR2Files(path):
    # this function exists to exclude par2s formatted as such:
    # filename.vol000+01.par2
    # this regex will match those for exclusion:
    par2_regex = ".vol\d+[-+]\d+."

    result = []
    folders = []
    if ( not os.path.isdir(path) ): return False

    for f in os.listdir(path):
        ff = os.path.join(path, f)

        if ( os.path.isdir(ff) ): 
            folders.append(ff)
            continue

        if f.lower().endswith(".par2"):
            if re.search(par2_regex, f, re.IGNORECASE): continue
            result.append(ff)
            continue            

    for f in folders: result += getRARFiles(f)
    return result
    
def par2Folder(path):
    result = False

    # Generate a list of rar_file
    par2_files = getPAR2Files(path)
    for par2_file in par2_files:
        mt.log.info("Checking PAR2 file: " + par2_file)

        # run par2 command and report results.
        f = par2_file.replace(" ", "\ ").replace("(", "\(").replace(")", "\)")
        output = mt.utils.execute("/usr/bin/par2 r " + f)
        result = getLastLine(output)

    return result
