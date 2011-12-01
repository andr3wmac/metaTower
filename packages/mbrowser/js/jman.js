$('#mbrowser_main').dialog({
	autoOpen: false, 
	minWidth: 400,
	minHeight: 250
});

$( "#mbrowser_external_link" ).dialog({
	resizable: false,
	height:145,
	modal: true,
	buttons: {
		"Close": function() {
			$('#mbrowser_external_link').dialog("close");
		}
	},
	autoOpen: false
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
        var html = "<li class='video'><img onclick='mbrowser.toggleInfo(this)' class='icon' src='mbrowser/images/mtfile.png'>";
        html += "<div class='name'><a href=':" + paths[i] + "'>" + names[i] + "</a></div>";
        html += "<div class='info'>";
        html += "<ul><li><a href='#' onclick='mbrowser.getExternalLink(\"" + paths[i] + "\");'>Generate External Link</a></li><li><a href='#'>Convert to Web Video</a></li></ul>";
        html += "</div></li>";
		mt.html("mbrowser_content", html, true);
	}
};

mbrowser.toggleInfo = function(element)
{
    var info = element.parentNode.children[2];
    if ( info.style.display == "block" )
    {
        info.style.display = "none";
    } else {
        info.style.display = "block";
    }
};

mbrowser.getExternalLink = function(link)
{
    mt("mbrowser.getExternalLink('" + link + "')");
};

mbrowser.externalLink = function(elink)
{
    $("#mbrowser_external_link").dialog("open");
    $("#mbrowser_external_link_text").html("<a href='" + elink + "'>Link to File.</a>");
    //jman.createClipboardLink("balls", "this was copied.");
};
