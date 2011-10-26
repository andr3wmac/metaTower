$('#package_manager_main').dialog({
	autoOpen: false, 
	minWidth: 400,
	minHeight: 250
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

package_manager.data = function(id, package_name, status, version, description) {
	package_manager.hideMenu();
	document.getElementById("package_manager_content").innerHTML = "";

	// layout of the package information.
	mt.html("package_manager_content", "<li><b>" + package_name + "</b> ( " + id + " v" + version + " )</li>", true);
	mt.html("package_manager_content", "<li>" + description + "</li>", true);

	mt.html("package_manager_content", "<li></li>", true);

	if ( status == "0" )
		mt.html("package_manager_content", "<li class='menu' onclick='package_manager.reload(\"" + id + "\")'>Reload Package</li>", true);
		mt.html("package_manager_content", "<li class='menu' onclick='package_manager.disable(\"" + id + "\")'>Disable Package</li>", true);
		mt.html("package_manager_content", "<li class='menu' onclick='package_manager.delete(\"" + id + "\")'>Delete Package</li>", true);
	if ( status == "1" )
		mt.html("package_manager_content", "<li class='menu' onclick='package_manager.update(\"" + id + "\")'>Update Package</li>", true);
	if ( status == "2" )
		mt.html("package_manager_content", "<li class='menu' onclick='package_manager.install(\"" + id + "\")'>Install Package</li>", true);

	// return to main menu
	mt.html("package_manager_content", "<li class='menu' onclick='package_manager.showMenu()'>Return to Main Menu</li>", true);
};
