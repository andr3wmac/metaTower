$('#nzbfind_main').dialog({
	autoOpen: false, 
	minWidth: 530,
	minHeight: 400
});

mt.progress("nzbfind_progress", 50);

nzbfind.showMenu = function()
{
	$("#nzbfind_menu").show();
	$("#nzbfind_content").hide();
}
nzbfind.hideMenu = function()
{
	$("#nzbfind_content").show();
	$("#nzbfind_menu").hide();
};

nzbfind.showStatus = function()
{
    var sBar = document.getElementById("nzbfind_statusbar");
    sBar.style.display = "block";
    var pBody = document.getElementById("nzbfind_body");
    pBody.style.bottom = "38px";
};

nzbfind.hideStatus = function()
{
    var sBar = document.getElementById("nzbfind_statusbar");
    sBar.style.display = "none";
    var pBody = document.getElementById("nzbfind_body");
    pBody.style.bottom = "8px";
};

