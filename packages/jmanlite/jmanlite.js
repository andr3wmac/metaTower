var jmanlite = {
    // Quick function to scroll to the top.
    top: function()
    {
        window.scrollTo(0,0);
    },

	menu_items: [],
	MenuItem: function()
	{
		this.caption = "";
		this.package_name = "";
		this.on_click = "";
	},

	menu: function(caption, package_name)
	{
		var item = new this.MenuItem();
		item.caption = caption;
		item.package_name = package_name;
		this.menu_items.push(item);

		mt.html("jmanlite_taskbar", "<li><a onClick=\"jmanlite.menuClicked('" + package_name + "');\" href=\"#\">" + caption + "</a></li>", true);
	},

	menuClicked: function(package_name)
	{
		for ( i = 0; i < this.menu_items.length; i++ )
		{
			var entry = this.menu_items[i];
			if ( entry.package_name == package_name )
			{
				mt("event('jmanlite.menu." + package_name + "')")
			}
		}
	}
};
