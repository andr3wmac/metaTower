$('#mbrowser_main').dialog({
	autoOpen: false, 
	minWidth: 400,
	minHeight: 250
});

mbrowser.showMenu = function()
{
	$("#mbrowser_menu").show();
	$("#mbrowser_content").hide();
}
mbrowser.hideMenu = function()
{
	$("#mbrowser_content").show();
	$("#mbrowser_menu").hide("blind");
};

mbrowser.data = function(paths, names) {
	mbrowser.hideMenu();
	document.getElementById("mbrowser_content").innerHTML = "";
	mt.html("mbrowser_content", "<li class='menu' onclick='mbrowser.showMenu()'>Return to Main Menu</li>", true);
	for (i=0; i < paths.length; i++)
	{
		mt.html("mbrowser_content", "<li class='video'><a href=':" + paths[i] + "'>" + names[i] + "</a></li>", true);
	}
};
