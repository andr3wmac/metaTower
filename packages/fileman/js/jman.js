$('#fileman_main').dialog({
	autoOpen: false, 
	minWidth: 400,
	minHeight: 250
});

$( "#fileman_confirm_delete" ).dialog({
	resizable: false,
	height:145,
	modal: true,
	buttons: {
		"Delete": function() {
			fileman.jman.confirmDelete();
			$( this ).dialog( "close" );
		},
		Cancel: function() {
			$( this ).dialog( "close" );
		}
	},
	autoOpen: false
});

$('#fileBrowser').selectable();

fileman.data = function(path, dirs, files) {
	mt.html("fileBrowser", "", false);

	if ( fileman.current_path == "" ) fileman.home_path = path;
	fileman.current_path = path;

    p = document.getElementById("fmanPath");
    p.value = path;

	for(i = 0; i < dirs.length; i++) {
		mt.html("fileBrowser", "<li class='folder' ondblclick='fileman.openFolder(\"" + dirs[i] + "\");'>" + dirs[i] + "</li>", true);
	}
	for(i = 0; i < files.length; i++) {
        var f_path = path + "/" + files[i];
		mt.html("fileBrowser", "<li class='file'><a href=':" + f_path + "'>" + files[i] + "</a></li>", true);
	}
};

fileman.jman = {
    deleteQueue: [],
	deleteSelected: function() {
		$( "#fileman_confirm_delete" ).dialog("open");
        var selected_items = [];
        $('.ui-selected').each( function() { selected_items.push("'" + $.trim($(this).html()) + "'"); } );
        this.deleteQueue = selected_items;
	},
	confirmDelete: function() {
		$( "#fileman_confirm_delete" ).dialog("hide");
        mt("fileman.delete('" + fileman.current_path + "', [" + this.deleteQueue + "])");
	}
};

fileman.onPathKeyPress = function(e) {
    var key=e.keyCode;
    if (key==13){
        p = document.getElementById("fmanPath");
        fileman.go(p.value);
    }
}
