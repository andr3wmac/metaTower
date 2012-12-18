var searchpkg = {
    search_results: {},
    
    keyup: function(e)
    {   
        if ( e.keyCode == 13 )
          	searchpkg.query();
    },

    status: function(msg, progress)
	{
		mt.html("search_status", msg, false);
        if ( progress >= 0 )
            searchpkg.showStatus()
            mt.progress("search_progress", progress );
        if ( progress >= 100 )
            setTimeout("searchpkg.hideStatus()", 2000);
	},

	query: function()
    {
        var query = document.getElementById("search_query").value;
        mt("search.query('" + query + "', " + searchpkg.EngineList.selected + ")");
        searchpkg.status("Searching...", 0);
    },

	save: function(id)
    {
        mt("search.save('" + id + "', " + searchpkg.EngineList.selected + ")");
        searchpkg.status("Saving..", 0);

        var e = document.getElementById("search_" + id);
        if ( e ) e.className = "nzb_downloaded";
    },

    save_complete: function()
    {
        searchpkg.status("Done.", 100);
    },

    data: function(results)
    {
        searchpkg.search_results = results;

        // set result counts
        searchpkg.EngineList.clearResultCounts();
        for ( index in results )
        {
            result_count = results[index].length;
            if ( result_count == 0 ) continue;
            searchpkg.EngineList.setResultCount(index, result_count);
        }

        // show results
        searchpkg.showResults();
        searchpkg.status("Done.", 100);
    },

    showResults: function()
    {   
        var results = searchpkg.search_results[searchpkg.EngineList.selected];
        if ( !results ) return;
        
        var html = "";
        for ( var i = 0; i < results.length; i++ )
        {
            var result = results[i];
            var dl_class = "nzb";
            if ( result.downloaded == "True" ) dl_class = "nzb_downloaded"; 
            html += "<li id='search_" + result.id  + "' class='" + dl_class + "'><a href='#!' onClick='searchpkg.save(\"" + result.id + "\");'>" + result.name + " (<b>" + result.size + "</b>)</a></li>";
        }

        mt.html("search_results", html, false);
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

searchpkg.EngineList = {
    selected: 0,
    count: 0,

    set: function(list)
    {
        list_html = "";
        searchpkg.EngineList.count = list.length;

        for(var x = 0; x < list.length; x++)
        {
            if ( x == searchpkg.selected )
            {
                list_html += "<li><a id='search_engine" + x + "' href='#!' style='font-weight: bold;' ";
                list_html += "onclick='searchpkg.EngineList.select(" + x + ");'>" + list[x] + "</a>";
                list_html += "<span id='search_engine" + x + "_count'></span></li>";
            }            
            else
            {            
                list_html += "<li><a id='search_engine" + x + "' href='#!' ";
                list_html += "onclick='searchpkg.EngineList.select(" + x + ");'>" + list[x] + "</a>";
                list_html += "<span id='search_engine" + x + "_count'></span></li>";
            }        
        }

        mt.html("search_engines", list_html, false);
        searchpkg.EngineList.select(0);
    },

    select: function(index)
    {
        for(var x = 0; x < searchpkg.EngineList.count; x++)
        {
            var e = document.getElementById("search_engine" + x);
            if ( e ) e.style.fontWeight = (index == x) ? "bold" : "normal";
        }
        searchpkg.EngineList.selected = index;
        searchpkg.showResults();
    },

    setResultCount: function(index, rcount)
    {
        var e = document.getElementById("search_engine" + index + "_count");
        e.innerHTML = "&nbsp;(" + rcount + ")";
    },

    clearResultCounts: function()
    {
        for(var x = 0; x < searchpkg.EngineList.count; x++)
        {
            var e = document.getElementById("search_engine" + x + "_count");
            if ( e ) e.innerHTML = "";
        }
    }
};
