import mt, os, re

def process_nzb(item):
    # attempt to par2.
    par2_result = par2Folder(item.save_to)
    if ( par2_result == False ): item.par2_results = "No par2 files found."
    else: item.par2_results = par2_result

    # attempt to unrar.
    item.unrar_results = "Decompressing files.."
    unrar_result = unrarFolder(item.save_to)
    if ( unrar_result == False ): item.unrar_results = "No rar files found."
    else: item.unrar_results = unrar_result

    # scan directory for files we wish to keep.
    save_to = mt.config["dlmanager/nzb/save_to"]
    save_exts = mt.config["dlmanager/save_files"].lower()    
    for f in os.listdir(item.save_to):
        ext = os.path.splitext(f)[1]        
        if ( ext.lower() in save_exts ):
            mt.utils.move(os.path.join(item.save_to, f), os.path.join(save_to, f))

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
    unrar = mt.config["dlmanager/nzb/unrar"]
    results = {}
    extract_files = {}
    rar_files = getRARFiles(path)

    # Generate a list of files to be extracted.
    for rar_file in rar_files:
        rar_flist = mt.utils.execute([unrar, "lb", rar_file]).splitlines()
        for f in rar_flist:
            if ( f != "" ) and ( not extract_files.has_key(f) ):
                extract_files[f] = rar_file

    # Narrow that list down to just the rar files to be extracted.
    rar_files = mt.utils.removeDuplicates(extract_files.values())

    # Now we actually extract them, only the last result will be shown.
    for rar_file in rar_files:
        mt.log.info("Extracting RAR file: " + rar_file)
        rar_file = mt.utils.escapePath(rar_file)
        output = mt.utils.execute([unrar, "e", "-o+", "-ts0", rar_file, path])
        last_line = getLastLine(output)

        if ( results.has_key(last_line) ):
            results[last_line] += 1
        else:
            results[last_line] = 1

    result = ""
    result_count = 0
    for r in results:
        if ( results[r] > result_count ):
            result = r
            result_count = results[r]
    if ( result_count > 1 ):
        result = result + " (" + str(result_count) + "/" + str(len(rar_files)) + ")"
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
    par2 = mt.config["dlmanager/nzb/par2"]
    results = {}

    # Generate a list of rar_file
    par2_files = getPAR2Files(path)
    for par2_file in par2_files:
        mt.log.info("Checking PAR2 file: " + par2_file)
        par2_file = mt.utils.escapePath(par2_file)
        output = mt.utils.execute([par2, "r", par2_file])

        last_line = getLastLine(output)
        if ( results.has_key(last_line) ):
            results[last_line] += 1
        else:
            results[last_line] = 1

    result = ""
    result_count = 0
    for r in results:
        if ( results[r] > result_count ):
            result = r
            result_count = results[r]
    if ( result_count > 1 ):
        result = result + " (" + str(result_count) + "/" + str(len(par2_files)) + ")"
    return result
