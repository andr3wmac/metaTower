
var mp3extract = {
    completed: [],

    addYoutube: function()
    {
        var url = document.getElementById("youtube_url").value;
        mt("mp3extract.add('" + url + "')"); 
    },

	youtube: function(id, title, state, progress)
	{
		// the actual output
		var youtube_element = document.getElementById(id);

        // Check if its been removed.
        if ( state == -1 )
        {
		    if ( youtube_element )
		    {
		        var parent = youtube_element.parentNode;
		        parent.removeChild(youtube_element);
            }
            return;
        }

		if ( !youtube_element )
		{
			mt.html("mp3extract_content", "<li id=\"" + id + "\" class=\"mp3extract_item\"></li>", true);
            mt.html(id, "<img onclick=\"mp3extract.toggleMenu('" + id + "')\" class='mp3extract_icon' src='mp3extract/images/youtube.png'>", false);
            mt.html(id, "<span id=\"" + id + "_file\"></span><br><span id=\"" + id + "_message\"></span><div id=\"prog_" + id + "\"></div>", true);
			youtube_element = document.getElementById(id);
		}

        switch(state)
        {
            // Queued.
		    case 0:
			    mt.html(id + "_file", "<b>" + title + "</b>", false);
                mt.html(id + "_message", "Queued.", false);
			    mt.progress("prog_" + id, 0);	
		        break;

            // Downloading.
		    case 1:
                mt.html(id + "_file", "<b>" + title + "</b>", false);
                mt.html(id + "_message", "Downloading..", false);
			    mt.progress("prog_" + id, progress);	
		        break;

            // Converting.
		    case 2:
                mt.html(id + "_file", "<b>" + title + "</b>", false);
                mt.html(id + "_message", "Converting..", false);
			    mt.progress("prog_" + id, progress);	
		        break;

            // Completed.
		    case 3:
                mt.html(id + "_file", "<b>" + title + "</b>", false);
                mt.html(id + "_message", "Completed.", false);
			    mt.progress("prog_" + id, -1);	
		        break;
		};
	},

    toggleMenu: function(id)
    {
        var menu = document.getElementById("menu_" + id);
        if ( menu == null )
        {
            var html = "<div id='menu_" + id + "' class='mp3extract_item_menu'><ul>";
            html += "<li><a href='#' onclick='mp3extract.remove(\"" + id + "\");'>Remove</a></li>";
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
		mt("mp3extract.remove('" + id + "')");
	},

    removeCompleted: function()
    {
        mt("mp3extract.remove_completed()");
    }
};

mp3extract.update = function()
{
    setTimeout("mp3extract.sendUpdate();", 1000);
};

mp3extract.sendUpdate = function() {
	mt("mp3extract.update()");
};

mp3extract.sendUpdate();
