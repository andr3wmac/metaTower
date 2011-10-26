package_manager.showMenu = function()
{
	var menu = document.getElementById("package_manager_menu");
	menu.style.display = "block";
	var content = document.getElementById("package_manager_content");
	content.style.display = "none";
};
package_manager.hideMenu = function()
{
	var menu = document.getElementById("package_manager_menu");
	menu.style.display = "none";
	var content = document.getElementById("package_manager_content");
	content.style.display = "block";
};

package_manager.data = function(paths, names) {
	package_manager.hideMenu();
	document.getElementById("package_manager_content").innerHTML = "";
	mt.html("package_manager_content", "<li class='menu' onclick='package_manager.showMenu()'>Return to Main Menu</li>", true);
	for (i=0; i < paths.length; i++)
	{
		mt.html("package_manager_content", "<li class='video'><a href=':" + paths[i] + "'>" + names[i] + "</a></li>", true);
	}
};
