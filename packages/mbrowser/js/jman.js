$('#mbrowser_main').dialog({
	autoOpen: false, 
	minWidth: 400,
	minHeight: 250
});

$('#mbrowser_player').dialog({
	autoOpen: false, 
	minWidth: 664,
	minHeight: 358,
    resizable: false
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

mbrowser.openWebVideo = function(f)
{
    var html = "<div id='player'>";
    html += "<object id='f4Player' width='640' height='360' type='application/x-shockwave-flash' data='mbrowser/f4player/player.swf'> ";
    html += "<param name='movie' value='mbrowser/f4player/player.swf' /> ";
    html += "<param name='quality' value='high' /> ";
    html += "<param name='menu' value='false' /> ";
    html += "<param name='scale' value='noscale' /> ";
    html += "<param name='allowfullscreen' value='true'>";
    html += "<param name='allowscriptaccess' value='always'>";
    html += "<param name='swlivevonnect' value='true' /> ";
    html += "<param name='cachebusting' value='false'>";
    html += "<param name='flashvars' value='skin=mbrowser/f4player/skin.swf&video=../../../:" + f + "'/> ";
    html += "</object></div>";

    mt.html("mbrowser_player", html, false);
    jman.dialog("mbrowser_player");
};
