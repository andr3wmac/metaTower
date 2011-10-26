var package_manager = {
	status: function(msg)
	{
		mt.html("package_manager_status", msg, false);
	},

	refresh: function()
	{
		package_manager.status("Refreshing sources..");
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
		package_manager.status("Installing " + id + "..");
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
