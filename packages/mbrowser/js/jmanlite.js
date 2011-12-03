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

mbrowser.showStatus = function()
{
    var sBar = document.getElementById("mbrowser_statusbar");
    sBar.style.display = "block";
};
mbrowser.hideStatus = function()
{
    var sBar = document.getElementById("mbrowser_statusbar");
    sBar.style.display = "none";
};

mbrowser.openWebVideo = function(f)
{
    var html = "<li class='menu' onclick='mbrowser.showMenu()'>Return to Main Menu</li>";
    html += "<li><div id='player' style='text-align:center'>";
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
    html += "</object></div></li>";

    mt.html("mbrowser_content", html, false);
};
