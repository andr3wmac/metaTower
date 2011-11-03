fileman.data = function(path, dirs, files)
{
	if ( fileman.current_path == "" ) fileman.home_path = path;
	fileman.current_path = path;

	var fileBrowser = document.getElementById("fileBrowser");
	fileBrowser.innerHTML = "";

	var level_up = document.createElement("li");
	level_up.className = "folder";
	level_up.innerHTML = "..";
	level_up.onclick = function () { fileman.up(); };
	fileBrowser.appendChild(level_up);

	for(i = 0; i < dirs.length; i++)
	{
		var child = document.createElement("li");
		child.className = "folder";
		child.innerHTML = dirs[i];
		child.onclick = Function("fileman.openFolder('" + dirs[i] + "');");
		fileBrowser.appendChild(child);
	}
	for(i = 0; i < files.length; i++)
	{
		var child = document.createElement("li");
		child.className = "file";
		child.innerHTML = "<a href=':" + path + "/" + files[i] + "' target='_self'>" + files[i] + "</a>";
		fileBrowser.appendChild(child);
	}
}
