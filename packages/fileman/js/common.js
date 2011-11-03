var fileman = {
	home_path: "",
	current_path: "",
	openFolder: function(foldername) {
		mt("fileman.openFolder(\"" + this.current_path + "\", \"" + foldername + "\")"); 
	},
	up: function() {
		mt("fileman.folderUp(\"" + this.current_path + "\")"); 
	},
	home: function () {
		if ( this.home_path ) {
			//switchPath(this.home_path);
		}
	}
};
