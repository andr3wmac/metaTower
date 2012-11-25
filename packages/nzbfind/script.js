var nzbfind = {
    category: '0',
    categories: ['tv-all', '6', '41', '7', 'movies-all', '2', '42'],
    setCat: function(num) 
    { 
        nzbfind.category = nzbfind.categories[num];
        for(var x = 0; x < nzbfind.categories.length; x++)
        {
            var e = document.getElementById("nzbfind_menu" + x);
            if ( x == num )
            {
                e.style.fontWeight = "bold";
            }
            else
            {
                e.style.fontWeight = "normal";   
            }
        }
    },

    keyup: function(e)
    {   
        if ( e.keyCode == 13 )
          	nzbfind.search();
    },

    status: function(msg, progress)
	{
		mt.html("nzbfind_status", msg, false);
        if ( progress >= 0 )
            nzbfind.showStatus()
            mt.progress("nzbfind_progress", progress );
        if ( progress >= 100 )
            setTimeout("nzbfind.hideStatus()", 2000);
	},

	search: function()
    {
        var query = document.getElementById("nzbfind_query").value;
        mt("nzbfind.search('" + query + "', '" + nzbfind.category + "')");
        nzbfind.status("Searching...", 0);
    },

	download: function(id)
    {
        mt("nzbfind.download(" + id + ")");
        nzbfind.status("Downloading..", 0);
    },

    dl_complete: function()
    {
        nzbfind.status("Done.", 100);
    },

    data: function(results)
    {
        var html = "";
        for ( var i = 0; i < results.length; i++ )
        {
            var result = results[i];
            html += "<li class='nzb' onClick='nzbfind.download(" + result.id + ")'>" + result.name + " (<b>" + result.size + "</b>)</li>";
        }
        mt.html("nzbfind_results", html, false);
        nzbfind.status("Done.", 100);
    },
};

nzbfind.showStatus = function()
{
    var sBar = document.getElementById("nzbfind_statusbar");
    sBar.style.display = "block";
};

nzbfind.hideStatus = function()
{
    var sBar = document.getElementById("nzbfind_statusbar");
    sBar.style.display = "none";
};
