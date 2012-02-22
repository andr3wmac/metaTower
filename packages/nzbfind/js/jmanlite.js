nzbfind.showMenu = function()
{
	var menu = document.getElementById("nzbfind_menu");
	menu.style.display = "block";
	var content = document.getElementById("nzbfind_content");
	content.style.display = "none";
};
nzbfind.hideMenu = function()
{
	var menu = document.getElementById("nzbfind_menu");
	menu.style.display = "none";
	var content = document.getElementById("nzbfind_content");
	content.style.display = "block";
};

nzbfind.showStatus = function()
{
    var sBar = document.getElementById("nzbfind_statusbar");
    sBar.style.display = "block";
};

nzbfind.hideStatus = function()
{
    var sBar = document.getElementById("nzbfind_statusbar");
    sBar.style.display = "none";
};
