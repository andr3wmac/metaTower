var mbrowser = {
	allAudio: function() { mt("mbrowser.query('audio')"); },
	newAudio: function() { mt("mbrowser.query('audio', True, 50)"); },
	allVideo: function() { mt("mbrowser.query('video')"); },
	newVideo: function() { mt("mbrowser.query('video', True, 50)"); },

    tv: function(show, season)
    {
        if ( show )
        {
            if ( season ) mt("mbrowser.tvQuery('" + show + "', '" + season + "')");
            else mt("mbrowser.tvQuery('" + show + "')");
        }
        else
            mt("mbrowser.tvQuery()");
    },

    toggleInfo: function(id)
    {
        var info = document.getElementById(id + "_info");
        if ( info == null )
        {
            var html = "<div id='" + id + "_info' class='info' style='display:block;'>";
            html += "<ul><li><a id='" + id + "_elink' href='#' onclick=\"mbrowser.getExternalLink('" + id + "');\">Generate External Link</a></li>";
            html += "<li><a id='" + id + "_webvideo' href='#' onclick=\"mbrowser.webConvert('" + id + "');\">Convert to Web Video</a></li></ul>";
            html += "</div>";
            mt.html(id, html, true);
        } else {
            if ( info.style.display == "none" )
            {
                info.style.display = "block";
            } else {
                info.style.display = "none";
            }
        }
    },

    getExternalLink: function(id)
    {
        mt("mbrowser.getExternalLink('" + id + "')");
    },
    externalLink: function(id, elink)
    {
        var e = document.getElementById(id + "_elink");
        e.innerHTML = "External Link";
        e.setAttribute("onclick", "");
        e.href = elink;
    },

    webVideo: function(id, weblink)
    {
        var e = document.getElementById(id + "_webvideo");
        e.innerHTML = "Play Web Video";
        e.setAttribute("onclick", "mbrowser.openWebVideo('" + weblink + "')");
        e.href = weblink;
    },
    webConvert: function(id)
    {
        mt("mbrowser.convertToWeb('" + id + "')");
    },

    refresh: function()
    {
        mbrowser.status("Refreshing..", 0);
        mt("mbrowser.refreshLibrary()");
    },
    refreshComplete: function()
    {
        mbrowser.status("Refresh Complete.", 100);
    },

    statusUpdate: function(message, percent)
    {
        mbrowser.status(message, percent);
        if ( percent < 100 )
            setTimeout("mt(\"mbrowser.status()\")", 500);
    },
    status: function(msg, progress)
    {
        mbrowser.showStatus()
	    mt.html("mbrowser_status", msg, false);
        if ( progress >= 0 )
            mt.progress("mbrowser_progress", progress );
        if ( progress >= 100 )
            setTimeout("mbrowser.hideStatus()", 2000);
    }
};

mbrowser.data = function(contents, returnLine)
{
    mbrowser.hideMenu();
    document.getElementById("mbrowser_content").innerHTML = "";

    var html = "<li class='menu' onclick='mbrowser.showMenu()'>Return to Main Menu</li>";
    if ( returnLine ) html = returnLine;

    for (var i = 0; i < contents.length; i++)
    {
        var item = contents[i];
        var id = item["id"];
        //mbrowser.library[item["id"]] = item;

        html += "<li class='video' id='" + id + "'>";
        html += "<img onclick=\"mbrowser.toggleInfo('" + item["id"] + "')\" class='icon' src='mbrowser/images/mtfile.png'>";
        html += "<div class='name'><a href=':" + item["path"] + "'>" + item["name"] + "</a></div>";

        if ( item["web"] || item["external"] )
        {
            html += "<div id='" + id + "_info' class='info' style='display: none;'>";

            if ( item["external"] )
                html += "<ul><li><a id='" + id + "_elink' href='" + item["external"] + "'>External Link</a></li>";
            else
                html += "<ul><li><a id='" + id + "_elink' href='#' onclick=\"mbrowser.getExternalLink('" + id + "');\">Generate External Link</a></li>";

            if ( item["web"] )
                html += "<li><a id='" + id + "_webvideo' href='#' onclick=\"mbrowser.openWebVideo('" + item["web"] + "');\">Play Web Video</a></li></ul>";
            else
                html += "<li><a id='" + id + "_webvideo' href='#' onclick=\"mbrowser.webConvert('" + id + "');\">Convert to Web Video</a></li></ul>";

            html += "</div>";
        }

        html += "</li>";
    }
    mt.html("mbrowser_content", html, true);
};


mbrowser.tvData = function(show, contents)
{
    mbrowser.data(contents, "<li class='menu' onclick='mbrowser.tv(\"" + show + "\");'>Return to " + show + "</li>");
};
mbrowser.tvShows = function(shows)
{
    mbrowser.hideMenu();
    document.getElementById("mbrowser_content").innerHTML = "";
    var html = "<li class='menu' onclick='mbrowser.showMenu()'>Return to Main Menu</li>";
    for (var i = 0; i < shows.length; i++)
    {
        var show = shows[i];
        html += "<li class='show' onclick=\"mbrowser.tv('" + show + "');\">" + show + "</li>";
    }
    mt.html("mbrowser_content", html, true);
};

mbrowser.tvSeasons = function(show, seasons)
{
    document.getElementById("mbrowser_content").innerHTML = "";
    var html = "<li class='menu' onclick=\"mbrowser.tv();\">Return to TV Shows</li>";
    for (var i = 0; i < seasons.length; i++)
    {
        var season = seasons[i];
        html += "<li class='season' onclick=\"mbrowser.tv('" + show + "', '" + season + "');\">" + show + " - Season " + season + "</li>";
    }
    mt.html("mbrowser_content", html, true);
};
