import ctypes, os

libboost_thread = None
libboost_system = None
libboost_filesystem = None
libboost_system = None
libtorrent_rasterbar = None
libtorrent = None

def getLibrary():
    global libboost_thread, libboost_system, libboost_filesystem, libboost_system, libtorrent_rasterbar, libtorrent

    if ( not libtorrent ):
        path = os.path.dirname(__file__)
        libboost_thread = ctypes.CDLL(os.path.join(path, "libboost_thread.so.1.46.1"))
        libboost_system = ctypes.CDLL(os.path.join(path, "libboost_system.so.1.46.1"))
        libboost_filesystem = ctypes.CDLL(os.path.join(path, "libboost_filesystem.so.1.46.1"))
        libboost_system = ctypes.CDLL(os.path.join(path, "libboost_system.so.1.46.1"))
        libboost_rasterbar = ctypes.CDLL(os.path.join(path, "libtorrent-rasterbar.so.6"))

        import libtorrent

    return libtorrent
