$('#dlmanager_main').dialog({
	autoOpen: false, 
	minWidth: 650,
	minHeight: 200,
});

$('#dlmanager_content').selectable();

dlmanager.sendUpdate = function() {
	if ( $("#dlmanager_main").parents(".ui-dialog").is(":visible") )
	{
		mt("dlmanager.update()");
	}
};

dlmanager.jman = {
	removeSelected: function()
	{
		var toBeRemoved = ""
		$('.ui-selected').each( function() { toBeRemoved += $.trim($(this).attr("id")) + ","; $(this).hide(); } );
		mt("dlmanager.remove_selected('" + toBeRemoved + "')");
	},

	toggleUpload: function()
	{
		var upload = document.getElementById("dlmanager_upload");
		var upload_toggle = document.getElementById("dlmanager_upload_toggle");
		if ( upload.style.display == "none" )
		{
			upload.style.display = "block";
			upload_toggle.style.display = "none";
		} else {
			upload.style.display = "none";
			upload_toggle.style.display = "block";
		}
	}
};
