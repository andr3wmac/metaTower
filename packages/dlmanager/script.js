
var dlmanager = {
    completed: [],
	nzb: function(id, filename, state, args)
	{
		// the actual output
		var nzb_element = document.getElementById(id);

        // Check if its been removed.
        if ( state == -1 )
        {
		    if ( nzb_element )
		    {
		        var parent = nzb_element.parentNode;
		        parent.removeChild(nzb_element);
            }
            return;
        }

        // Check if its been created.
		if ( !nzb_element )
		{
			mt.html("dlmanager_content", "<li id=\"" + id + "\" class=\"dlmanager_item\"></li>", true);
			nzb_element = document.getElementById(id);
            mt.html(id, "<img onclick=\"dlmanager.toggleMenu('" + id + "')\" class='dlmanager_icon' src='dlmanager/images/nzb.png'>", true);
            mt.html(id, "<span id=\"" + id + "_file\"></span><br><span id=\"" + id + "_message\"></span><div id=\"prog_" + id + "\"></div>", true);
            mt.progress("prog_" + id, 0);
		};
        
        switch ( state )
        {

		    // Queued.
		    case 0:
                mt.html(id + "_file", "<b>" + filename + "</b>", false);
                mt.html(id + "_message", "Queued.", false);
			    mt.progress("prog_" + id, 0);
		        break;

		    // Downloading.
		    case 1:
                mt.html(id + "_file", "<b>" + filename + "</b> ( " + args["completed"] + "/" + args["total"] + " MB )", false);
                mt.html(id + "_message", "Downloading at " + args["dl_rate"] + "kb/s", false);
                mt.progress("prog_" + id, args["percent"]);
                break;

		    // Assembly
		    case 2:
                mt.html(id + "_file", "<b>" + filename + "</b>", false);
                mt.html(id + "_message", "Assembling files..", false);
                mt.progress("prog_" + id, args["assembly_percent"]);
		        break;

		    // Error
		    case 3:
			    mt.html(id, "<b>" + filename + "</b><br>Failed<div id=\"prog_" + id + "\"></div>", false);
			    mt.progress("prog_" + id, 0);
		        break;

		    // Completed
		    case 4:
                dlmanager.completed.push(id);
                var par2_element = document.getElementById(id + "_par2");
                var unrar_element = document.getElementById(id + "_unrar");
                if ( !par2_element || !unrar_element )
                {
                    mt.html(id, "<img onclick=\"dlmanager.toggleMenu('" + id + "')\" class='dlmanager_icon' src='dlmanager/images/nzb.png'>", false);
                    mt.html(id, "<b>" + filename + "</b><br><img src=\"dlmanager/images/par2.png\" width=\"16\" height=\"16\" style=\"padding-right: 5px\"><span><span id=\"" + id + "_par2\"></span><br><img src=\"dlmanager/images/unrar.png\" width=\"16\" height=\"16\" style=\"padding-right: 5px\"><span id=\"" + id + "_unrar\"></span></span>", true);
                    par2_element = document.getElementById(id + "_par2");
                    unrar_element = document.getElementById(id + "_unrar");
                }

			    mt.html(id + "_par2", args["par2"]);
                mt.html(id + "_unrar", args["unrar"]);
		        break;
        };
	},

	torrent: function(id, filename, state, args)
	{
		// the actual output
		var torrent_element = document.getElementById(id);

        // Check if its been removed.
        if ( state == -1 )
        {
		    if ( torrent_element )
		    {
		        var parent = torrent_element.parentNode;
		        parent.removeChild(torrent_element);
            }
            return;
        }

		if ( !torrent_element )
		{
			mt.html("dlmanager_content", "<li id=\"" + id + "\" class=\"dlmanager_item\"></li>", true);
            mt.html(id, "<img onclick=\"dlmanager.toggleMenu('" + id + "')\" class='dlmanager_icon' src='dlmanager/images/torrent.png'>", false);
            mt.html(id, "<span id=\"" + id + "_file\"></span><br><span id=\"" + id + "_message\"></span><div id=\"prog_" + id + "\"></div>", true);
			torrent_element = document.getElementById(id);
		}

        switch(state)
        {
            // Queued.
		    case 0:
			    mt.html(id + "_file", "<b>" + filename + "</b>", false);
                mt.html(id + "_message", "Queued.", false);
			    mt.progress("prog_" + id, 0);	
		        break;

            // Downloading.
		    case 1:
                mt.html(id + "_file", "<b>" + filename + "</b>", false);

                html = args["msg"];
                html += "  <i>DL</i>: " + args["dl_rate"] + " kb/s";
                html += "  <i>UL</i>: " + args["ul_rate"] + " kb/s";
                html += "  <i>Peers</i>: " + args["peers"];
                mt.html(id + "_message", html, false);

			    mt.progress("prog_" + id, args["progress"]);	
		        break;

            // Completed.
		    case 2:
			    mt.html(id + "_file", "<b>" + filename + "</b>", false);
                mt.html(id + "_message", "Completed. Seeding.", false);
			    mt.progress("prog_" + id, 100);	
                break;
    
            // Other Status, display.
		    default:
                mt.html(id + "_file", "<b>" + filename + "</b>", false);
                mt.html(id + "_message", state, false);
			    mt.progress("prog_" + id, 0);
		};
	},

    toggleMenu: function(id)
    {
        var menu = document.getElementById("menu_" + id);
        if ( menu == null )
        {
            var html = "<div id='menu_" + id + "' class='dlmanager_item_menu'><ul>";
            html += "<li><a href='#' onclick='dlmanager.remove(\"" + id + "\");'>Remove</a></li>";
            html += "<li><a href='#'>Move to bottom</a></li>";
            html += "</ul>";
            mt.html(id, html, true);
        } else {
            if ( menu.style.display == "none" )
            {
                menu.style.display = "block";
            } else {
                menu.style.display = "none";
            }
        }
    },

	remove: function(id)
	{
		mt("dlmanager.remove('" + id + "')");
	},

    removeCompleted: function()
    {
        mt("dlmanager.remove_completed()");
    }
};

dlmanager.update = function()
{
    setTimeout("dlmanager.sendUpdate();", 1000);
};

dlmanager.sendUpdate = function() {
	mt("dlmanager.update()");
};

dlmanager.sendUpdate();
