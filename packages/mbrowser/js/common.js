var mbrowser = {
	allAudio: function() { mt("mbrowser.query({'type': 'audio'})"); },
	newAudio: function() { mt("mbrowser.query({'type': 'audio'}, True, 50)"); },
	allVideo: function() { mt("mbrowser.query({'type': 'video'})"); },
	newVideo: function() { mt("mbrowser.query({'type': 'video'}, True, 50)"); },
    movies: function() { mt("mbrowser.query({'type': 'video', 'vidtype': 'movie'})"); },

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
            var file = document.getElementById(id + "_file");
            var f_args = file.href.split("/");
            var f = f_args[f_args.length-1];
            var html = mbrowser.getInfoHTML(id, f, null, null, true);
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

    toggleRename: function(id)
    {
        var rename = document.getElementById(id + "_rename");
        var rename_toggle = document.getElementById(id + "_renametoggle");
        if ( rename.style.display == "none" )
        {
            rename.style.display = "list-item";
            rename_toggle.style.display = "none";
        }
        else
        {
            rename.style.display = "none";
            rename_toggle.style.display = "list-item";
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
    },

    getFileHTML: function(item)
    {
        var id = item["id"];

        var html = "<li class='video' id='" + id + "'>";
        html += "<img onclick=\"mbrowser.toggleInfo('" + item["id"] + "')\" class='icon' src='mbrowser/images/mtfile.png'>";
        html += "<div class='name'><a id='" + id + "_file' href=':" + item["path"] + "'>" + item["name"] + "</a></div>";

        var f_args = item["path"].split("/");
        var f = f_args[f_args.length-1];
        html += mbrowser.getInfoHTML(id, f, item["external"], item["web"]);

        html += "</li>";
        return html;
    },
    getInfoHTML: function(id, file, elink, webvid, visible)
    {
        var html = "";
    
        // Should it be visible?
        if ( visible )
            html += "<div id='" + id + "_info' class='info' style='display: block;'><ul>";
        else
            html += "<div id='" + id + "_info' class='info' style='display: none;'><ul>";

        // Rename
        if ( file )
        {
            html += "<li id='" + id + "_renametoggle'><a href='#' onclick='mbrowser.toggleRename(\"" + id + "\")'>Rename</a></li>";
            html += "<li id='" + id + "_rename' style='display: none;'><input id='" + id + "_renameinp' class='rename_input' type='text' name='lastname' value='" + file + "'/>";
            html += "<a href='#' onclick='mbrowser.rename(\"" + id + "\");'>Save</a> | <a href='#' onclick='mbrowser.toggleRename(\"" + id + "\")'>Hide</a></li>";
        }

        // Do we have an external link?
        if ( elink )
            html += "<li><a id='" + id + "_elink' href='" + elink + "'>External Link</a></li>";
        else
            html += "<li><a id='" + id + "_elink' href='#' onclick=\"mbrowser.getExternalLink('" + id + "');\">Generate External Link</a></li>";

        // Is a web version available?
        if ( webvid )
            html += "<li><a id='" + id + "_webvideo' href='#' onclick=\"mbrowser.openWebVideo('" + webvid + "');\">Play Web Video</a></li>";
        else
            html += "<li><a id='" + id + "_webvideo' href='#' onclick=\"mbrowser.webConvert('" + id + "');\">Convert to Web Video</a></li>";

        html += "</ul></div>";
        return html;
    },
    rename: function(id)
    {
        var new_name = document.getElementById(id + "_renameinp").value;
        mt("mbrowser.rename('" + id + "', '" + new_name + "')");
    }
};

mbrowser.data = function(contents, returnLine)
{
    mbrowser.hideMenu();
    document.getElementById("mbrowser_content").innerHTML = "";

    var html = "<li class='menu' onclick='mbrowser.showMenu()'>Return to Main Menu</li>";
    if ( returnLine ) html = returnLine;

    for (var i = 0; i < contents.length; i++)
        html += mbrowser.getFileHTML(contents[i])

    mt.html("mbrowser_content", html, true);
};

mbrowser.updateFile = function(id, values)
{
    var f = document.getElementById(id + "_file");
    if ( values["name"] ) f.innerHTML = values["name"];
    if ( values["path"] ) f.href = values["path"];
    if ( values["external"] ) mbrowser.externalLink(id, values["external"]);
    if ( values["web"] ) mbrowser.webVideo(id, values["web"]);
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
