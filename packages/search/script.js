var search = {
    setEngines: function(list)
    {
        list_html = "";
        for(var x = 0; x < list.length; x++)
        {
            var engine = list[x];
            list_html += "<li>" + engine + "</li>";
        }
        mt.html("search_engines", list_html, false);
    },

    keyup: function(e)
    {   
        if ( e.keyCode == 13 )
          	search.query();
    },

    status: function(msg, progress)
	{
		mt.html("search_status", msg, false);
        if ( progress >= 0 )
            search.showStatus()
            mt.progress("search_progress", progress );
        if ( progress >= 100 )
            setTimeout("search.hideStatus()", 2000);
	},

	query: function()
    {
        var query = document.getElementById("search_query").value;
        mt("search.search('" + query + "')");
        search.status("Searching...", 0);
    },

	download: function(id)
    {
        alert("Got here!");
        mt("search.download(" + id + ")");
        search.status("Downloading..", 0);

        var e = document.getElementById("search_" + id);
        if ( e ) e.className = "nzb_downloaded";
    },

    dl_complete: function()
    {
        search.status("Done.", 100);
    },

    data: function(results)
    {
        var html = "";
        for ( var i = 0; i < results.length; i++ )
        {
            var result = results[i];
            var dl_class = "nzb";
            if ( result.downloaded == "True" ) dl_class = "nzb_downloaded"; 
            html += "<li id='search_" + result.id  + "' class='" + dl_class + "'><a href='#!' onClick='alert(search); search.download(" + result.id + ");'>" + result.name + " (<b>" + result.size + "</b>)</a></li>";
        }
        mt.html("search_results", html, false);
        search.status("Done.", 100);
    },
    
    showStatus: function()
    {
        var sBar = document.getElementById("search_statusbar");
        sBar.style.display = "block";
    },

    hideStatus: function()
    {
        var sBar = document.getElementById("search_statusbar");
        sBar.style.display = "none";
    }
};
