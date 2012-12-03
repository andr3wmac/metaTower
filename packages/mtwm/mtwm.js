var mtwm = {
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

    update: function(version, packages, quickbar, free_space)
    {
        var header = document.getElementById("home_header");
        header.innerHTML = "metaTower v" + version;
        
        var quickbar_list = {};
        var plist_html = "";
        var plist = document.getElementById("home_packagelist");
        if ( plist )
        {
            for(var package_name in packages)
            {
                var args = packages[package_name];             
                if ( args[1] )
                {
                    var package_html = "<li><a href='#!' onClick=\"" + args[1] + "\">" + args[0] + "</a>";
                    if ( args[2] )
                    {
                        quickbar_list[args[0]] = args[1]; 
                        package_html += "<a href='#!' onClick='mtwm.togglePin(\"" + package_name + "\")'><img src='mtwm/images/pin.png' /></a></li>";
                    }
                    else
                        package_html += "<a href='#!' onClick='mtwm.togglePin(\"" + package_name + "\")'><img src='mtwm/images/pin_trans.png' /></a></li>";            
                    plist_html += package_html;                
                }
                else
                    plist_html += "<li>" + args[0] + "<img src='mtwm/images/pin_trans.png' /></li>";
            }
            mt.html("home_packagelist", plist_html, false);
            mtwm.quickbar(quickbar_list);               
        }

        mt.html("home_main", "<p>Free Space: " + free_space + "</p>", false);
    }
};
