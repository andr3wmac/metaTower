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
    getExternalLink: function(link, returnElement)
    {
        var id = mt.uid();
        returnElement.setAttribute("id", id);
        mt("mbrowser.getExternalLink('" + link + "', '" + id + "')");
    },
    externalLink: function(elink, id)
    {
        var e = document.getElementById(id);
        e.innerHTML = "External Link";
        e.onclick = null;
        e.href = elink;
    }
};
