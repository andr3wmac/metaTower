import mt, os, commands

def unrarFolder(path):
    result = False
    folders = []
    if ( not os.path.isdir(path) ): return False

    for f in os.listdir(path):
        #if ( result != False ): break

        ff = os.path.join(path, f)
        if ( f.endswith(".rar") and os.path.isfile(ff) ):
            rar_file = ff.replace(" ", "\ ").replace("(", "\(").replace(")", "\)")
            try:
                output = commands.getoutput('/usr/bin/unrar e -o+ -ts0 ' + rar_file + " " + mt.config["dlmanager/nzb/save_to"])
                output_args = output.splitlines()
                result = output_args[len(output_args)-1]
            except:
                mt.log.error("Unrar error.")
        if ( os.path.isdir(ff) ): folders.append(ff)
    if ( result == False ):
        for f in folders: result = unrarFolder(f)
    return result
    
def par2Folder(path):
    result = False
    folders = []
    if ( not os.path.isdir(path) ): return False

    for f in os.listdir(path):
        #if ( result != False ): break

        ff = os.path.join(path, f)
        if ( f.endswith(".rar") and os.path.isfile(ff) ): 
            par2_file = ff.replace(" ", "\ ").replace("(", "\(").replace(")", "\)")[:-3] + "par2"
            try:
                output = commands.getoutput('/usr/bin/par2 r ' + par2_file)
                output_args = output.splitlines()
                result = output_args[len(output_args)-1]
            except:
                mt.log.error("Par2 error.")
            par2_file = ""
        if ( os.path.isdir(ff) ): folders.append(ff)
    if ( result == False ):
        for f in folders: result = par2Folder(f)
    return result
