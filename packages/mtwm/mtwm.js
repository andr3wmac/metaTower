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

    window: function(e, args)
    {
        if ( e )
        {
            e.className = "window";

            if ( args.header )
            {
                var e_header = document.getElementById(args.header);
                e_header.className = "header";
            }

            if ( args.footer )
            {
                var e_footer = document.getElementById(args.footer);
                e_footer.className = "footer";
            }
        }
    },

    spread: function(target, args)
    {
        if ( !args.columns ) return;
        var container = target.parentNode;

        var table = document.createElement("table");
        table.id = target.id;
        table.className = target.className;
        //mt.cloneAttributes(target, table);

        var tr = document.createElement("tr");
        table.appendChild(tr);

        for(var a = 0; a < args.columns.length; a++)
        {
            var e = document.getElementById(args.columns[a]);
            var parent = e.parentNode;
            var td = document.createElement("td");
            
            //mt.cloneAttributes(e, td);
            td.id = e.id;
            td.className = e.className;
            td.innerHTML = e.innerHTML;
            
            parent.removeChild(e);
            tr.appendChild(td);
        };

        container.insertBefore(table, target);
        container.removeChild(target);
    }
};

mt.addLayout("window", mtwm.window);
mt.addLayout("spread", mtwm.spread);

mtwm.home = {
    show: function()
    {
        // nothing yet.
    },

    hide: function()
    {
        // nothing yet.
    },

    update: function(version, packages, free_space)
    {
        var header = document.getElementById("home_header");
        header.innerHTML = "metaTower v" + version;

        var plist = document.getElementById("home_packagelist");
        if ( plist )
        {
            var plistHTML = "<ul>";
            for(var name in packages)
            {
                var func = packages[name];
                if ( func )
                    plistHTML += "<li><a onClick=\"" + func + "\">" + name + "</a></li>";
                else
                    plistHTML += "<li>" + name + "</li>";
            }
            plistHTML += "</ul>";
            plist.innerHTML = plistHTML;
        }

        var main = document.getElementById("home_main");
        main.innerHTML = "Free Space: " + free_space;
    }
};
