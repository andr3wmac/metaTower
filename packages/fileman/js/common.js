var fileman = {
	home_path: "",
	current_path: "",
	openFolder: function(foldername) {
		mt("fileman.openFolder(\"" + this.current_path + "\", \"" + foldername + "\")"); 
	},
	up: function() {
		mt("fileman.folderUp(\"" + this.current_path + "\")"); 
	},
    go: function(path)
    {
        mt("fileman.openFolder(\"" + path + "\", \"\")"); 
    },
	home: function () {
		mt("fileman.openFolder(\"~\", \"\")"); 
	}
};
