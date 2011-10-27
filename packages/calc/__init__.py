import mtCore as mt

def onLoad():
    mt.events.register("jman.load", jman_load)
    mt.events.register("jman.menu.calc", jman_menu)

def onUnload():
    mt.events.clear(jman_load)
    mt.events.clear(jman_menu)

def jman_load(session):
    mt.packages.jman.menu(session, "Calculator", 3)
    mt.packages.jman.taskbar(session, "Calculator", ["calc_man"], {"context1": "alert('yeah buddy!');"})

    out = session.out()
    out.htmlFile("calc/index.html", "body", True)
    out.jsFile("calc/script.js")
    return out
    
def jman_menu(session):
    out = session.out()
    out.js("jman.dialog('calc_main')");
    return out
