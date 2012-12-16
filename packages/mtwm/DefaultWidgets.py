import mt, Widget, time

class SystemMonitor(Widget.Widget):
    def __init__(self):
        self.name = "System Monitor"
        self.last_update = 0
        self.cpu_usage = 0
        self.ram_info = 0
        self.hdd_stats = 0

    def home(self, httpOut):
        return

    def updateStats(self):
        if ( time.time() - self.last_update < 60 ):
            return
        
        self.cpu_usage = mt.utils.getCPUUsage()
        self.ram_info = mt.utils.getRAMInfo()
        hdds = mt.utils.get_hdds()  
        self.hdd_stats = {"used": 0, "total": 0}
        for hdd in hdds:
            self.hdd_stats["used"] += hdd["used"]
            self.hdd_stats["total"] += hdd["total"]
        self.last_update = time.time()

    def update(self, httpOut):
        self.updateStats()
        httpOut.jsFunction("mtwm.home.updateSystemMonitor", self.cpu_usage, self.ram_info, self.hdd_stats)
