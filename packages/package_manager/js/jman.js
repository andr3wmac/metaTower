$('#package_manager_main').dialog({
	autoOpen: false, 
	minWidth: 530,
	minHeight: 400
});

$( "#package_manager_confirm" ).dialog({
	resizable: false,
	height:145,
	modal: true,
	buttons: {
		"Continue": function() {
			alert("Shit would be happening.");
			$( this ).dialog( "close" );
		},
		Cancel: function() {
			$( this ).dialog( "close" );
		}
	},
	autoOpen: false
});

mt.progress("package_manager_progress", 50);

package_manager.showMenu = function()
{
	$("#package_manager_menu").show();
	$("#package_manager_content").hide();
}
package_manager.hideMenu = function()
{
	$("#package_manager_content").show();
	$("#package_manager_menu").hide();
};

package_manager.installed = {};
package_manager.updates = {};
package_manager.available = {};

package_manager.packageList = function(installed, updates, available)
{
    package_manager.installed = installed;
    var installed_count = 0;
    for ( i in installed ) installed_count++;
    if ( installed_count > 0 )
        mt.html("package_manager_btnInstalled", "Installed (" + installed_count + ")", false)
    else
        mt.html("package_manager_btnInstalled", "Installed", false)

    package_manager.updates = updates;
    var update_count = 0;
    for ( i in updates ) update_count++;
    if ( update_count > 0 )
        mt.html("package_manager_btnUpdates", "Updates (" + update_count + ")", false)
    else
        mt.html("package_manager_btnUpdates", "Updates", false)

    package_manager.available = available;
    var available_count = 0;
    for ( i in available ) available_count++;
    if ( available_count > 0 )
        mt.html("package_manager_btnAvailable", "Available (" + available_count + ")", false)
    else
        mt.html("package_manager_btnAvailable", "Available", false)
};

package_manager.showInstalled = function()
{
    var html = "<li class='cat'>Installed Packages</li>";

    for ( package_id in package_manager.installed )
    {
        var package = package_manager.installed[package_id];
        html += "<li class='subcat' onClick='package_manager.getPackageInfo(\"" + package_id + "\");'>" + package + "</li>";
    }
    mt.html("package_manager_menu", html, false);
    package_manager.showMenu();
};

package_manager.showUpdates = function()
{
    var html = "<li class='cat'>Updates</li>";

    for ( package_id in package_manager.updates )
    {
        var package = package_manager.updates[package_id];
        html += "<li class='subcat' onClick='package_manager.getUpdateInfo(\"" + package_id + "\");'>" + package + "</li>";
    }
    mt.html("package_manager_menu", html, false);
    package_manager.showMenu();
};

package_manager.showAvailable = function()
{
    var html = "<li class='cat'>Available Packages</li>";

    for ( package_id in package_manager.available )
    {
        var package = package_manager.available[package_id];
        html += "<li class='subcat' onClick='package_manager.getInstallInfo(\"" + package_id + "\");'>" + package + "</li>";
    }
    mt.html("package_manager_menu", html, false);
    package_manager.showMenu();
};

package_manager.statusUpdate = function(message, percent)
{
    package_manager.status(message, percent);
    if ( percent < 100 )
        setTimeout("mt(\"package_manager.status()\")", 500);
};

package_manager.data = function(id, package_name, status, version, description) {
	package_manager.hideMenu();
	document.getElementById("package_manager_content").innerHTML = "";

	// layout of the package information.
	mt.html("package_manager_content", "<li><b>" + package_name + "</b> ( " + id + " v" + version + " )</li>", true);
	mt.html("package_manager_content", "<li>" + description + "</li>", true);

	mt.html("package_manager_content", "<li></li>", true);

	if ( status == "0" )
    {
		mt.html("package_manager_content", "<li class='menu' onclick='package_manager.reload(\"" + id + "\")'>Reload Package</li>", true);
		mt.html("package_manager_content", "<li class='menu' onclick='package_manager.disable(\"" + id + "\")'>Disable Package</li>", true);
		mt.html("package_manager_content", "<li class='menu' onclick='package_manager.delete(\"" + id + "\")'>Delete Package</li>", true);
    }
	if ( status == "1" )
		mt.html("package_manager_content", "<li class='menu' onclick='package_manager.update(\"" + id + "\")'>Update Package</li>", true);
	if ( status == "2" )
		mt.html("package_manager_content", "<li class='menu' onclick='package_manager.install(\"" + id + "\")'>Install Package</li>", true);

	// return to main menu
	mt.html("package_manager_content", "<li class='menu' onclick='package_manager.showMenu()'>Return to Main Menu</li>", true);
};
