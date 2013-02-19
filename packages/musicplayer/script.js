
var musicplayer = {
    play: function(src) {
        var audio = document.getElementById("audio");
        audio.style.display = "block";
        audio.src = src;
        audio.play();
    },

	allAudio: function() { 
        mt("musicplayer.query({'type': 'audio'})"); 
        return false;
    },
	newAudio: function() { 
        mt("musicplayer.query({'type': 'audio'}, True, 50)"); 
        return false;
    },

    toggleInfo: function(id)
    {
        var info = document.getElementById(id + "_info");
        if ( info == null )
        {
            var file = document.getElementById(id + "_file");
            var f_args = file.href.split("/");
            var f = f_args[f_args.length-1];
            var html = musicplayer.getInfoHTML(id, f, null, null, true);
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
        mt("musicplayer.getExternalLink('" + id + "')");
    },

    externalLink: function(id, elink)
    {
        var e = document.getElementById(id + "_elink");
        e.innerHTML = "External Link";
        e.setAttribute("onclick", "");
        e.href = elink;
    },

    refresh: function()
    {
        musicplayer.status("Refreshing..", 0);
        mt("musicplayer.refreshLibrary()");
        return false;
    },

    refreshComplete: function()
    {
        musicplayer.status("Refresh Complete.", 100);
    },

    statusUpdate: function(message, percent)
    {
        musicplayer.status(message, percent);
        if ( percent < 100 )
            setTimeout("mt(\"musicplayer.status()\")", 500);
    },

    status: function(msg, progress)
    {
        musicplayer.showStatus()
	    mt.html("musicplayer_status", msg, false);
        if ( progress >= 0 )
            mt.progress("musicplayer_progress", progress );
        if ( progress >= 100 )
            setTimeout("musicplayer.hideStatus()", 2000);
    },

    getFileHTML: function(item)
    {
        var id = item["id"];

        var html = "<li class='musicplayer_video' id='" + id + "'>";
        html += "<img onclick=\"musicplayer.toggleInfo('" + item["id"] + "')\" class='musicplayer_icon' src='musicplayer/images/mtfile.png'>";
        html += "<span class='musicplayer_name'><a id='" + id + "_file' href='#!' onclick='musicplayer.play(\"musicplayer/f/" + item["path"] + "\");'>" + item["name"] + "</a></span>";

        // 

        var f_args = item["path"].split("/");
        var f = f_args[f_args.length-1];
        html += musicplayer.getInfoHTML(id, f, item["external"], item["web"]);

        html += "</li>";
        return html;
    },

    getInfoHTML: function(id, file, elink, webvid, visible)
    {
        var html = "";
    
        // Should it be visible?
        if ( visible )
            html += "<div id='" + id + "_info' class='musicplayer_info' style='display: block;'><ul>";
        else
            html += "<div id='" + id + "_info' class='musicplayer_info' style='display: none;'><ul>";

        // Rename
        if ( file )
        {
            html += "<li id='" + id + "_renametoggle'><a href='#' onclick='musicplayer.toggleRename(\"" + id + "\")'>Rename</a></li>";
            html += "<li id='" + id + "_rename' style='display: none;'><input id='" + id + "_renameinp' class='musicplayer_rename' type='text' name='lastname' value='" + file + "'/>";
            html += "<a href='#' onclick='musicplayer.rename(\"" + id + "\");'>Save</a> | <a href='#' onclick='musicplayer.toggleRename(\"" + id + "\")'>Hide</a></li>";
        }

        html += "</ul></div>";
        return html;
    },
    rename: function(id)
    {
        var new_name = document.getElementById(id + "_renameinp").value;
        mt("musicplayer.rename('" + id + "', '" + new_name + "')");
    }
};

musicplayer.data = function(contents, returnLine)
{
    document.getElementById("musicplayer_main").innerHTML = "";

    var html = "";
    if ( returnLine ) html = returnLine;

    for (var i = 0; i < contents.length; i++)
        html += musicplayer.getFileHTML(contents[i])

    mt.html("musicplayer_main", html, true);
};

musicplayer.updateFile = function(id, values)
{
    var f = document.getElementById(id + "_file");
    if ( values["name"] ) f.innerHTML = values["name"];
    if ( values["path"] ) f.href = values["path"];
    if ( values["external"] ) musicplayer.externalLink(id, values["external"]);
    if ( values["web"] ) musicplayer.webVideo(id, values["web"]);
};

musicplayer.showStatus = function()
{
    var sBar = document.getElementById("musicplayer_statusbar");
    sBar.style.display = "block";
};
musicplayer.hideStatus = function()
{
    var sBar = document.getElementById("musicplayer_statusbar");
    sBar.style.display = "none";
};
