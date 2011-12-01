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

mbrowser.data = function(paths, names) {
	mbrowser.hideMenu();
	document.getElementById("mbrowser_content").innerHTML = "";
	mt.html("mbrowser_content", "<li class='menu' onclick='mbrowser.showMenu()'>Return to Main Menu</li>", true);
	for (i=0; i < paths.length; i++)
	{
		//mt.html("mbrowser_content", "<li class='video'><a href=':" + paths[i] + "'>" + names[i] + "</a></li>", true);
        var html = "<li class='video'><img onclick='mbrowser.toggleInfo(this)' class='icon' src='mbrowser/images/mtfile.png'>";
        html += "<div class='name'><a href=':" + paths[i] + "'>" + names[i] + "</a></div>";
        html += "<div class='info'>";
        html += "<ul><li><a href='#' onclick='mbrowser.getExternalLink(\"" + paths[i] + "\", this);'>Generate External Link</a></li><li><a href='#'>Convert to Web Video</a></li></ul>";
        html += "</div></li>";
		mt.html("mbrowser_content", html, true);
	}
};
