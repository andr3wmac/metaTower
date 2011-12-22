dlmanager.update = function()
{
    setTimeout("dlmanager.sendUpdate();", 1000);
};

dlmanager.sendUpdate = function() {
	mt("dlmanager.update()");
};
