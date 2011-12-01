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
