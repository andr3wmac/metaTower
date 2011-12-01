var mbrowser = {
	allAudio: function() { mt("mbrowser.query('audio')"); },
	newAudio: function() { mt("mbrowser.query('audio', True, 50)"); },
	allVideo: function() { mt("mbrowser.query('video')"); },
	newVideo: function() { mt("mbrowser.query('video', True, 50)"); },
    toggleInfo: function(id)
    {
        var info = document.getElementById(id + "_info");
        if ( info == null )
        {
            var html = "<div id='" + id + "_info' class='info'>";
            html += "<ul><li><a id='" + id + "_elink' href='#' onclick=\"mbrowser.getExternalLink('" + id + "');\">Generate External Link</a></li>";
            html += "<li><a id='" + id + "_webvideo' href='#'>Convert to Web Video</a></li></ul>";
            html += "</div>";
            mt.html(id, html, true);
        } else {
            if ( info.style.display == "block" )
            {
                info.style.display = "none";
            } else {
                info.style.display = "block";
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
    }
};

mbrowser.data = function(contents)
{
    mbrowser.hideMenu();
    document.getElementById("mbrowser_content").innerHTML = "";
    mt.html("mbrowser_content", "<li class='menu' onclick='mbrowser.showMenu()'>Return to Main Menu</li>", true);
    for (var i = 0; i < contents.length; i++)
    {
        var item = contents[i];
        //mbrowser.library[item["id"]] = item;

        var html = "<li class='video' id='" + item["id"] + "'>";
        html += "<img onclick=\"mbrowser.toggleInfo('" + item["id"] + "')\" class='icon' src='mbrowser/images/mtfile.png'>";
        html += "<div class='name'><a href=':" + item["path"] + "'>" + item["name"] + "</a></div>";
        html += "</li>";
	    mt.html("mbrowser_content", html, true);
    }
};
