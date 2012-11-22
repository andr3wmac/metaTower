mt.layout("dlmanager", "window", {header: "dlmanager_header"} );
mt.layout("dlmanager_layout", "spread", {columns: ["dlmanager_menu", "dlmanager_main"] } );

var dlmanager = {
    completed: [],
	nzb: function(id, filename, state, args)
	{
		// the actual output
		var nzb_element = document.getElementById(id);
		if ( !nzb_element )
		{
			mt.html("dlmanager_content", "<li id=\"" + id + "\" class=\"dlmanager_nzb\"></li>", true);
            mt.html(id, "<img onclick=\"dlmanager.toggleMenu('" + id + "')\" class='icon' src='dlmanager/images/nzb.png'>", false);
			nzb_element = document.getElementById(id);
            mt.html(id, "<span id=\"" + id + "_file\"></span><br><span id=\"" + id + "_message\"></span><div id=\"prog_" + id + "\"></div>", false);
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
                    mt.html(id, "<b>" + filename + "</b><br><img src=\"dlmanager/images/par2.png\" width=\"16\" height=\"16\" style=\"padding-right: 5px\"><span id=\"" + id + "_par2\"></span><br><img src=\"dlmanager/images/unrar.png\" width=\"16\" height=\"16\" style=\"padding-right: 5px\"><span id=\"" + id + "_unrar\"></span>", false);
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
		if ( !torrent_element )
		{
			mt.html("dlmanager_content", "<li id=\"" + id + "\" class=\"dlmanager_torrent\"></li>", true);
			torrent_element = document.getElementById(id);
		}

        switch(state)
        {
            // Queued.
		    case 0:
			    mt.html(id, "<b>" + filename + "</b><br>Queued.<div id=\"prog_" + id + "\"></div>", false);
			    mt.progress("prog_" + id, 0);	
		        break;

            // Downloading.
		    case 1:
                var html = "<b>" + filename + "</b><br>";
                html += args["msg"];
                html += "  <i>DL</i>: " + args["dl_rate"] + " kb/s";
                html += "  <i>UL</i>: " + args["ul_rate"] + " kb/s";
                html += "  <i>Peers</i>: " + args["peers"];
                html += "<div id=\"prog_" + id + "\"></div>";
			    mt.html(id, html, false);
			    mt.progress("prog_" + id, args["progress"]);	
		        break;

            // Completed.
		    case 2:
			    mt.html(id, "<b>" + filename + "</b><br>Completed.<div id=\"prog_" + id + "\"></div>", false);
			    mt.progress("prog_" + id, 100);	
                break;
    
            // Other Status, display.
		    default:
			    mt.html(id, "<b>" + filename + "</b><br>" + state + "<div id=\"prog_" + id + "\"></div>", false);
			    mt.progress("prog_" + id, 0);
		};
	},

    toggleMenu: function(id)
    {
        var menu = document.getElementById(id + "menu_");
        if ( menu == null )
        {
            alert("toggle menu!");
            //var file = document.getElementById(id + "_file");
            //var f_args = file.href.split("/");
            //var f = f_args[f_args.length-1];
            //var html = mbrowser.getInfoHTML(id, f, null, null, true);
            //mt.html(id, html, true);
        } else {
            if ( menu.style.display == "none" )
            {
                menu.style.display = "block";
            } else {
                menu.style.display = "none";
            }
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

    removeCompleted: function()
    {
        //var comp = dlmanager.completed.join();
        //dlmanager.remove(comp);
        mt("dlmanager.remove_completed()");
        //dlmanager.completed = [];
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
