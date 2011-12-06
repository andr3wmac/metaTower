import mtCore as mt

def onLoad():
    mt.events.register("jman.load", jman_load)
    mt.events.register("jman.menu.calc", jman_menu)

def onUnload():
    mt.events.clear(jman_load)
    mt.events.clear(jman_menu)

def jman_load(resp):
    mt.packages.jman.menu(resp.session, "Calculator", 0)
    mt.packages.jman.taskbar(resp.session, "Calculator", ["calc_main"], {"context1": "alert('yeah buddy!');"})

    resp.htmlFile("calc/index.html", "body", True)
    resp.jsFile("calc/script.js")
    
def jman_menu(resp):
    resp.js("jman.dialog('calc_main')");
