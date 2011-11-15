# I didn't want users to have to install anything it should work right out of the box.
# Therefore, I created this little abomination to load up libtorrent.

import ctypes, os, sys
def getLibrary():
    # Check to see if it's already loaded.
    try:
        if ( sys.modules.has_key("libtorrent") ): return sys.modules["libtorrent"]
    except:
        pass

    # Try this the easy way. This will work on either windows ( libtorrent.pyd ) or
    # if python-libtorrent is installed.
    try:
        import libtorrent
        return libtorrent
    except:
        pass

    # If we're still here it's not installed, and we're probably not on windows
    # otherwise it would have imported the .pyd file. Let's try one more thing..
    try:
        if ( os.name == "posix" ):
            path = os.path.dirname(__file__)
            libboost_python = ctypes.CDLL(os.path.join(path, "libboost_python-py27.so.1.46.1"))
            libboost_thread = ctypes.CDLL(os.path.join(path, "libboost_thread.so.1.46.1"))
            libboost_system = ctypes.CDLL(os.path.join(path, "libboost_system.so.1.46.1"))
            libboost_filesystem = ctypes.CDLL(os.path.join(path, "libboost_filesystem.so.1.46.1"))
            libboost_system = ctypes.CDLL(os.path.join(path, "libboost_system.so.1.46.1"))
            libboost_rasterbar = ctypes.CDLL(os.path.join(path, "libtorrent-rasterbar.so.6"))
            import libtorrent
            return libtorrent
    except:
        pass

    # At this point it's all failed, torrents will be disabled.
    return None
