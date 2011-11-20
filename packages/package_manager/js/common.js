var package_manager = {
	status: function(msg, progress)
	{
		mt.html("package_manager_status", msg, false);
        if ( progress >= 0 )
            mt.progress("package_manager_progress", progress );
	},

	refresh: function()
	{
		package_manager.status("Refreshing sources..", 0);
		mt("package_manager.refresh()");
	},

	getPackageInfo: function(id)
	{
		mt("package_manager.getPackageInfo('" + id + "')");
	},

	getUpdateInfo: function(id)
	{
		mt("package_manager.getUpdateInfo('" + id + "')");
	},

	getInstallInfo: function(id)
	{
		mt("package_manager.getInstallInfo('" + id + "')");
	},

	update: function(id)
	{
		package_manager.status("Updating " + id + "..");
		mt("package_manager.update('" + id + "')");
	},

	install: function(id)
	{
		package_manager.status("Connecting..", 0);
		mt("package_manager.install('" + id + "')");
	},

	reload: function(id)
	{
		package_manager.status("Reloading " + id + "..");
		mt("package_manager.reload('" + id + "')");
	},

	disable: function(id)
	{
		package_manager.status("Disabling " + id + "..");
		mt("package_manager.disable('" + id + "')");
	},

	delete: function(id)
	{
		package_manager.status("Deleting " + id + "..");
		mt("package_manager.delete('" + id + "')");
	}
};
