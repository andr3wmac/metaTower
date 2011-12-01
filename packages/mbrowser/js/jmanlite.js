mbrowser.showMenu = function()
{
	var menu = document.getElementById("mbrowser_menu");
	menu.style.display = "block";
	var content = document.getElementById("mbrowser_content");
	content.style.display = "none";
};
mbrowser.hideMenu = function()
{
	var menu = document.getElementById("mbrowser_menu");
	menu.style.display = "none";
	var content = document.getElementById("mbrowser_content");
	content.style.display = "block";
};
