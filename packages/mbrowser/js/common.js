var mbrowser = {
	allAudio: function() { mt("mbrowser.query('audio')"); },
	newAudio: function() { mt("mbrowser.query('audio', True, 50)"); },
	allVideo: function() { mt("mbrowser.query('video')"); },
	newVideo: function() { mt("mbrowser.query('video', True, 50)"); },
    toggleInfo: function(element)
    {
        var info = element.parentNode.children[2];
        if ( info.style.display == "block" )
        {
            info.style.display = "none";
        } else {
            info.style.display = "block";
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
        var html = "<li class='video' id='" + item["id"] + "'><img onclick='mbrowser.toggleInfo(this)' class='icon' src='mbrowser/images/mtfile.png'>";
        html += "<div class='name'><a href=':" + item["path"] + "'>" + item["name"] + "</a></div>";
        html += "<div class='info'>";
        html += "<ul><li><a id='" + item["id"] + "_elink' href='#' onclick=\"mbrowser.getExternalLink('" + item["id"] + "');\">Generate External Link</a></li>";
        html += "<li><a id='" + item["id"] + "_webvideo' href='#'>Convert to Web Video</a></li></ul>";
        html += "</div></li>";
	    mt.html("mbrowser_content", html, true);
    }
};
