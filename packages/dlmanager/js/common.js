var dlmanager = {
	nzb: function(id, filename, status, total, completed, percent, dl_rate, par2, unrar)
	{
		// the actual output
		var nzb_element = document.getElementById(id);
		if ( !nzb_element )
		{
			mt.html("dlmanager_content", "<li id=\"" + id + "\" class=\"dlmanager_nzb\"></li>", true);
			nzb_element = document.getElementById(id);
		}
		// Queued.
		if ( status == 0 )
		{
			mt.html(id, "<b>" + filename + "</b><br>Queued<div id=\"prog_" + id + "\"></div>", false);
			mt.progress("prog_" + id, 0);
		}
		// Downloading.
		if ( status == 1 )
		{
            if ( completed > total ) { completed = total; }
            if ( percent >= 100 )
            {
			    mt.html(id, "<b>" + filename + "</b> ( " + completed + "/" + total + " MB )<br>Decoding..<div id=\"prog_" + id + "\"></div>", false);
			    mt.progress("prog_" + id, 100);
            }
            else
            {
                mt.html(id, "<b>" + filename + "</b> ( " + completed + "/" + total + " MB )<br>Downloading at " + dl_rate + "kb/s<div id=\"prog_" + id + "\"></div>", false);
                mt.progress("prog_" + id, percent);
            }
		}
		// Completed
		if ( status == 2 )
		{
			mt.html(id, "<b>" + filename + "</b><br><img src=\"dlmanager/images/par2.png\" width=\"16\" height=\"16\" style=\"padding-right: 5px\">" + par2 + "<br><img src=\"dlmanager/images/unrar.png\" width=\"16\" height=\"16\" style=\"padding-right: 5px\">" + unrar, false);
		}
		// Error
		if ( status == 3 )
		{
			mt.html(id, "<b>" + filename + "</b><br>Failed<div id=\"prog_" + id + "\"></div>", false);
			mt.progress("prog_" + id, 0);
		}
	},

	torrent: function(id, filename, state, progress, dl_rate)
	{
		// the actual output
		var torrent_element = document.getElementById(id);
		if ( !torrent_element )
		{
			mt.html("dlmanager_content", "<li id=\"" + id + "\" class=\"dlmanager_torrent\"></li>", true);
			torrent_element = document.getElementById(id);
		}

		if ( state == 0 )
		{
			mt.html(id, "<b>" + filename + "</b><br>Queued.<div id=\"prog_" + id + "\"></div>", false)
			mt.progress("prog_" + id, 0);	
		} 
		else if ( state == 1 )
		{
			mt.html(id, "<b>" + filename + "</b><br>Downloading at " + dl_rate + "<div id=\"prog_" + id + "\"></div>", false);
			mt.progress("prog_" + id, progress);	
		}
		else if ( state == 2 )
		{
			mt.html(id, "<b>" + filename + "</b><br>Completed.<div id=\"prog_" + id + "\"></div>", false)
			mt.progress("prog_" + id, 100);	
		} else {
			mt.html(id, "<b>" + filename + "</b><br>" + state + "<div id=\"prog_" + id + "\"></div>", false)
			mt.progress("prog_" + id, 0);
		}
	},

	remove: function(selected)
	{
		var items = selected.split(",");
		for(i = 0; i < items.length; i++)
		{
			if ( items[i] == "" ) continue;
			var element = document.getElementById(items[i]);
			if ( element )
			{
				var parent = element.parentNode;
				parent.removeChild(element);
			}
		}
	},

	update: function()
	{
		setTimeout("dlmanager.sendUpdate();", 1000);
	}
};
