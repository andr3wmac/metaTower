mt.layout("nzbfind", "window", {header: "mbrowser_header"} );
mt.layout("nzbfind_layout", "spread", {columns: ["nzbfind_menu", "nzbfind_main"] } );

var nzbfind = {
    category: '0',
    setCat: function(cat) 
    { 
        nzbfind.category = cat; 
        nzbfind.hideMenu(); 
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
        nzbfind.status("Downloading NZB..", 0);
    },

    dl_complete: function()
    {
        nzbfind.status("Done. Check your download manager.", 100);
    },

    data: function(results)
    {
        var html = "<li class='menu' onclick='nzbfind.showMenu()''>Return to Main Menu</li>";
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
