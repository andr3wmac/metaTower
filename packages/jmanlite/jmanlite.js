var jmanlite = {
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
        var item = new this.MenuItem();
        item.caption = caption;
        item.package_name = package_name;
       

        var e = document.createElement("li");
        e.innerHTML = "<a onClick=\"jmanlite.menuClicked('" + package_name + "');\" href=\"#\">" + caption + "</a>";
        document.getElementById("jmanlite_taskbar").appendChild(e);
       
        item.element = e;
        this.menu_items.push(item);
        //mt.html("jmanlite_taskbar", "<li>, true);
    },

    menuClicked: function(package_name)
    {
        for ( i = 0; i < this.menu_items.length; i++ )
        {
            var entry = this.menu_items[i];
            if ( entry.package_name == package_name )
            {
                mt("event('jmanlite.menu." + package_name + "')")
                entry.element.style.fontWeight = "bold";
            } else {
                entry.element.style.fontWeight = "normal";
            }
        }
    }
};
