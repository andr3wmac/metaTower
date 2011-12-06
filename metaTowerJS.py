"""
 * metaTower v0.3.5
 * http://www.metatower.com
 *
 * Copyright 2011, Andrew W. MacIntyre
 * http://www.andrewmac.ca
 * Licensed under GPL v3.
 * See license.txt 
 *  or http://www.metatower.com/license.txt
"""
# contains the metaTower.js file, this way it can be compiled into the program.
content = """
mt = function(url, target_override)
{
	if ( !url ) { return; }
	var page_request = false;
	if (window.XMLHttpRequest) // if Mozilla, Safari etc
		page_request = new XMLHttpRequest();
	else if (window.ActiveXObject){ // if IE
		try { page_request = new ActiveXObject("Msxml2.XMLHTTP");} 
		catch (e){
			try{ page_request = new ActiveXObject("Microsoft.XMLHTTP"); }
			catch (e){}
		}
	} else {
		alert("failed to ajax.");
	}
	page_request.onreadystatechange=function(){ mt.response(page_request, target_override); };
	page_request.open("GET", "!" + url, true);
	page_request.send(null);
};

mt.load = function()
{
	mt("pageLoaded()");
    //window.onerror = mt.error;
};

mt.timed = function(url, time, target_override)
{
	setTimeout("mt('" + url + "', '" + target_override + "');", time);
};

mt.refresh = function(time)
{
    if ( time ) setTimeout("location.reload(true);", time)
    else location.reload(true);
};

mt.uid = function()
{
  var s = [], itoh = '0123456789ABCDEF';
 
  // Make array of random hex digits. The UUID only has 32 digits in it, but we
  // allocate an extra items to make room for the '-'s we'll be inserting.
  for (var i = 0; i <36; i++) s[i] = Math.floor(Math.random()*0x10);
 
  // Conform to RFC-4122, section 4.4
  s[14] = 4;  // Set 4 high bits of time_high field to version
  s[19] = (s[19] & 0x3) | 0x8;  // Specify 2 high bits of clock sequence
 
  // Convert to hex chars
  for (var i = 0; i <36; i++) s[i] = itoh[s[i]];
 
  // Insert '-'s # removed.
  s[8] = s[13] = s[18] = s[23] = '';
 
  return s.join('');
};

mt.response = function(request, target_override)
{
    	if (request.readyState == 4) 
    	{
    		dataIn = request.responseText;

		    var strPos = 0;
		    if ( dataIn.substr(0, 4) == "!mt:" )
		    {
			    var intStr = "";
			    for(strPos = 4; strPos < dataIn.length; strPos++)
			    {
				    var chr = dataIn.charAt(strPos);
				    if ( chr == ';' ) { strPos++; break; }
				
				    intStr += chr;
			    }
			
			    var allData = dataIn.substr(strPos + parseInt(intStr), dataIn.length - strPos + parseInt(intStr));
			    var dataLocations = dataIn.substr(strPos, parseInt(intStr)).split(";");
			
			    for( dataPos = 0; dataPos < dataLocations.length; dataPos++ )
			    {
				    if ( dataLocations[dataPos] == "" ) continue;
				
				    var args = dataLocations[dataPos].split(":");
				    var locationArgs = args[1].split(",");
				
				    var pos = locationArgs[0];
				    var len = locationArgs[1];
				
				    var data = allData.substr(pos, len);
				
				    if ( args[0] == "html" )
				    {
					    var target = locationArgs[2];
					    var append = false;
					    if ( target.charAt(0) == "+" )
					    {
						    target = target.substr(1, target.length -1);
						    append = true;
					    }
					    mt.html(target, data, append);
				    } else {
					    if ( args[0] == "css" ) mt.css(data);
					    if ( args[0] == "js" ) mt.js(data);
				    }
			    }
		    }
    	}
};

// these functions were created to be overridden
// for example using the following as is will break jQuery dialogs, etc
// so another .js file is included to override the functions with jQuery
// specific methods. However these will work fine with an average html page.

mt.html = function(targetID, data, append)
{
	var target = null;
	if ( targetID == "" || !targetID || targetID == "body" ) target = document.body;
	else target = document.getElementById(targetID);
	
	if ( append ) target.innerHTML += data;
	else target.innerHTML = data;
};

mt.js = function(data)
{
	//var head = document.getElementsByTagName("head")[0]; 
	//var newScript = document.createElement('script');
	//newScript.type = "text/javascript";
	//newScript.innerHTML = data;
	//head.appendChild(newScript);
	if ( window.execScript )
	{
		window.execScript(data);
	} else {
		window.eval(data);
	}
};

mt.css = function(data)
{
	var head = document.getElementsByTagName("head")[0]; 
	var newScript = document.createElement('style');
	newScript.type = 'text/css';
	newScript.innerHTML = data;
	head.appendChild(newScript);
};

mt.progress = function(id, progress)
{
	var prog = document.getElementById(id + "_progress");
	if ( !prog )
	{
		var shell = document.getElementById(id);
		shell.className = "progressBar";
		prog = document.createElement("div");
		prog.id = id + "_progress";
		prog.className = "progressBar_progress";
		shell.appendChild(prog);
	}	
	prog.style.width = Math.round(progress) + "%";
};

mt.value = function(id, value)
{
    if ( value )
        document.getElementById(id).value = value;
    else
        return document.getElementById(id).value;
};

mt.removeValueFromArray = function(array, value)
{
    newArray = [];
    for ( i = 0; i < array.length; i++ )
        if ( array[i] != value ) newArray.push(array[i]);
    return newArray;
};

mt.error = function(err)
{
    alert("An error occured." + err);
};
"""
