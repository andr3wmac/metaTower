mt.load = function()
{
    mtwm.home.show();
};

var mtwm = {
    packages: {},

    menu_items: [],
    MenuItem: function()
    {
        this.caption = "";
        this.package_name = "";
        this.on_click = "";
        this.element = null;
    },

    menu: function(caption, package_name)
    {
        alert("menu: " + caption);

        var item = new this.MenuItem();
        item.caption = caption;
        item.package_name = package_name;

        var e = document.createElement("li");
        e.innerHTML = "<a onClick=\"mtwm.menuClicked('" + package_name + "');\" href=\"#\">" + caption + "</a>";
        document.getElementById("mtwm_taskbar").appendChild(e);
       
        item.element = e;
        this.menu_items.push(item);
        //mt.html("mtwm_taskbar", "<li>, true);
    },

    menuClicked: function(package_name)
    {
        for ( i = 0; i < this.menu_items.length; i++ )
        {
            var entry = this.menu_items[i];
            if ( entry.package_name == package_name )
                mt("event('mtwm.menu." + package_name + "')")
        }
    },

    quickbar: function(items)
    {
        var html = "<li><span class='icon' onClick='mtwm.home.show()'></span></li>";
        for(var item_name in items)
        {
            func = items[item_name];
            html += "<li><a href='#!' onClick=\"" + func + "\">" + item_name + "</a></li>";
        }
        mt.html("mtwm_quickbar", html, false); 
    },

    togglePin: function(package_name)
    {
        var e = document.getElementById("mtwm_pin_" + package_name);
        if ( e )
        {
            var img = e.getElementsByTagName("img")[0];
            if ( img.src.search("mtwm/images/pin_trans.png") > -1 )
                img.src = "mtwm/images/pin.png";
            else
                img.src = "mtwm/images/pin_trans.png";
        }
    
        mt("mtwm.togglePin(\"" + package_name + "\")");
    }
};

mtwm.home = {

    show: function()
    {
        mt("mtwm.home()");
    },

    hide: function()
    {
        // nothing yet.
    },

    update: function(version, packages, quickbar)
    {
        // 
        var plist = document.getElementById("home_packagelist");
        if ( plist )
        {
            // Package list.
            for(var package_name in packages)
            {
                var pkg_list_item = document.getElementById("mtwm_pkglist_" + package_name); 
                if ( pkg_list_item ) continue;

                var args = packages[package_name]; 
                var html = ""; 
                if ( args[1] )
                {
                    html += "<li id='mtwm_pkglist_" + package_name + "'>"
                    html += "<a href='#!' onClick=\"" + args[1] + "\">" + args[0] + "</a>";
                    
                    img_html = (args[2]) ? "<img src='mtwm/images/pin.png' />" : "<img src='mtwm/images/pin_trans.png' />";
                    html += "<a href='#!' style='display: none;' id='mtwm_pin_" + package_name + "' onClick='mtwm.togglePin(\"" + package_name + "\")'>" + img_html + "</a>"; 
                    html += "</li>";              
                }
                else
                    html += "<li>" + args[0] + "<img src='mtwm/images/pin_trans.png' /></li>";

                mt.html("home_packagelist", html, true);
            }

            // Load quickbar.            
            if ( quickbar )
            {
                var quickbar_list = {};
                for(var i = 0; i < quickbar.length; i++)
                {                
                    var pack_name = quickbar[i];
                    if ( pack_name == "" ) continue;
                    var pack = packages[pack_name];
                    quickbar_list[pack[0]] = pack[1];
                }
                mtwm.quickbar(quickbar_list);
            }

            mtwm.packages = packages;
        }
    },

    editQuickbar: function()
    {
        var e = document.getElementById("mtwm_edit_quickbar");
        var show = (e.innerHTML == "Edit Quickbar");        
        if ( show ) e.innerHTML = "Finish"
        else e.innerHTML = "Edit Quickbar" 

        for(var package_name in mtwm.packages)
        {
            var pin = document.getElementById("mtwm_pin_" + package_name);
            if ( pin )
            {
                if ( show ) pin.style.display = "inline";
                else pin.style.display = "none";
            }
        }  
    },

    updateSystemMonitor: function(cpu, ram, hdd)
    {
        var hdd_widget_html = "<div class='mtwm_widget mtwm_cpu'>"
        hdd_widget_html += "Harddrive: " + hdd["used"] + " / " + hdd["total"] + " GB<div id='mtwm_hdd_progress'></div><br>";
        hdd_widget_html += "CPU: " + cpu + "%<div id='mtwm_cpu_progress'></div><br>";
        hdd_widget_html += "Memory: " + ram["used"] + " / " + ram["total"] + " MB<div id='mtwm_ram_progress'></div>";
        hdd_widget_html += "</div>";
        mt.html("home_main", hdd_widget_html, false);
        mt.progress('mtwm_hdd_progress', (hdd["used"]/hdd["total"] * 100));        
        mt.progress('mtwm_cpu_progress', cpu);
        mt.progress('mtwm_ram_progress', (ram["used"]/ram["total"] * 100));
    }
};
