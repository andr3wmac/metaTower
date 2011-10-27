$(document).ready(function() {
	$.ui.draggable.prototype.options.top_boundary = 36;

    $.ui.draggable.prototype._setContainment = function() {
		var o = this.options;
		if(o.containment == 'parent') o.containment = this.helper[0].parentNode;
		if(o.containment == 'document' || o.containment == 'window') this.containment = [
		    (o.containment == 'document' ? 0 : $(window).scrollLeft()) - this.offset.relative.left - this.offset.parent.left,
		    (o.containment == 'document' ? o.top_boundary : $(window).scrollTop()) - this.offset.relative.top - this.offset.parent.top,
		    (o.containment == 'document' ? 0 : $(window).scrollLeft()) + $(o.containment == 'document' ? document : window).width() - this.helperProportions.width - this.margins.left,
		    (o.containment == 'document' ? 0 : $(window).scrollTop()) + ($(o.containment == 'document' ? document : window).height() || document.body.parentNode.scrollHeight) - this.helperProportions.height - this.margins.top
		];

		if(!(/^(document|window|parent)$/).test(o.containment) && o.containment.constructor != Array) {
		        var c = $(o.containment);
		    var ce = c[0]; if(!ce) return;
		    var co = c.offset();
		    var over = ($(ce).css("overflow") != 'hidden');

		    this.containment = [
		        (parseInt($(ce).css("borderLeftWidth"),10) || 0) + (parseInt($(ce).css("paddingLeft"),10) || 0),
		        (parseInt($(ce).css("borderTopWidth"),10) || 0) + (parseInt($(ce).css("paddingTop"),10) || 0),
		        (over ? Math.max(ce.scrollWidth,ce.offsetWidth) : ce.offsetWidth) - (parseInt($(ce).css("borderLeftWidth"),10) || 0) - (parseInt($(ce).css("paddingRight"),10) || 0) - this.helperProportions.width - this.margins.left - this.margins.right,
		        (over ? Math.max(ce.scrollHeight,ce.offsetHeight) : ce.offsetHeight) - (parseInt($(ce).css("borderTopWidth"),10) || 0) - (parseInt($(ce).css("paddingBottom"),10) || 0) - this.helperProportions.height - this.margins.top  - this.margins.bottom
		    ];
		    this.relative_container = c;

		} else if(o.containment.constructor == Array) {
		    this.containment = o.containment;
		}

    	};

	var open = $.ui.dialog.prototype.open;
	$.ui.dialog.prototype.open = function() {
		open.apply(this);
        jman.taskbar.onOpenDialog(this.element[0].id);
	};

	var close = $.ui.dialog.prototype.close;
	$.ui.dialog.prototype.close = function() {
		close.apply(this);
		jman.taskbar.onCloseDialog(this.element[0].id);
	};
});

mt.html = function(targetID, data, append)
{
	var target = null;
	if ( targetID == "body" ) target = $("body");
	else target = $("#" + targetID);
	
	if ( append ) target.append(data);
	else target.html(data);
}

mt.js = function(data)
{
	$('head').append("<script type='text/javascript'>" + data + "</script>");
}

mt.css = function(data)
{
	$('head').append("<style type='text/css'>" + data + "</style>");
}

mt.progress = function(id, progress)
{
	$("#" + id).progressbar({value: progress});
}

var jman = {
	menu: {
        items: [],
	    MenuItem: function()
	    {
            this.package_name = "";
		    this.caption = "";
		    this.priority = 5;
		    this.onClick = "";
	    },
	    
        add: function(package_name, caption, priority, onClick)
	    {
		    var entry = new this.MenuItem();
            entry.package_name = package_name;
		    entry.caption = caption;
            entry.priority = priority;
            if ( onClick == "" ) onClick = "jman.menu.onClicked('" + package_name + "');";
            entry.onClick = onClick;
		    this.items.push(entry);

		    mt.html("jman_taskbar_main_contents", "<li><a onClick=\"" + entry.onClick + "\" href=\"#\">" + entry.caption + "</a></li>", true);
		    jman.taskbar.refresh();
	    },

        onClicked: function(package_name)
	    {
		    for ( i = 0; i < this.items.length; i ++ )
		    {
			    var entry = this.items[i];
			    if ( entry.package_name == package_name )
			    {
				    mt("event('jman.menu." + package_name + "')")
			    }
		    }
	    },
    },

    Package: function()
    {
        this.package_name = "";
        this.dialogs = [];
        this.context = {};
        this.opened_dialogs = [];
    },

	dialog: function(dname)
	{
		$("#" + dname).dialog("open");
	},

    taskbar: {

        items: [],
	    TaskbarItem: function()
	    {
            this.package_name = "";
		    this.caption = "";
		    this.dialogs = [];
		    this.context = {};

            this.opened_dialogs = [];
	    },
	    
        add: function(package_name, caption, dialogs, context)
	    {
		    var entry = new this.TaskbarItem();
            entry.package_name = package_name;
		    entry.caption = caption;
            entry.dialogs = dialogs;
            entry.context = context;
		    this.items.push(entry);
		    this.refresh();
	    },

        onOpenDialog: function(id)
        {
            alert("Dialog opened:" + id);
        },
        onCloseDialog: function(id)
        {
            alert("Dialog closed:" + id);
        },
        refresh: function()
        {
	        for ( a = 0; a < this.items.length; a++ )
	        {
		        item = this.items[a];

		        show_item = false;
		        for ( b = 0; b < item.dialogs.length; b++ )
		        {
			        var dialog = $("#" + item.dialogs[b]).parents(".ui-dialog");
			        if ( dialog.is(":visible") ) { show_item = true; item.opened_dialogs.push(item.dialogs[b]); }
		        }
		        taskbar_entry = document.getElementById("jman_taskbar_" + item.package_name);
		        if (( taskbar_entry == null ) && ( show_item ))
		        {
			        entry_html = "<li style='z-index: 2000' id='jman_taskbar_" + item.package_name + "'><a href='#' onClick='jman.taskbar.onClicked(\"" +item.package_name + "\")'>" + item.caption + "</a><span></span><ul class='menu' style='display: none;'>"
			
			        // context menus
			        for ( var caption in item.context )
			        {
				        entry_html += "<li><a href='#' onClick='" + item.context[caption] + "'>" + caption + "</a></li>"
			        }
			        entry_html += "<li><a href='#' onClick='jman.taskbar.onClose(\"" + item.package_name + "\")'>Close</a></li>"

			        entry_html += "</ul></li><li>"
			        mt.html("jman_taskbar_contents", entry_html, true);
			        taskbar_entry = document.getElementById("jman_taskbar_" + item.package_name);
		        }
		        if ( taskbar_entry )
		        {
			        if ( show_item ) 
			        {
				        taskbar_entry.style.opacity = "1.0";
				        taskbar_entry.style.fontWeight = "bold";
			        } else {
				        taskbar_entry.style.opacity = "0.6";
				        taskbar_entry.style.fontWeight = "normal";
			        }
		        }
	        }

	        $("ul.jman_taskbar li span").click(function() { //When trigger is clicked...
		        //Drop down the menu on click
		        $(this).parent().find("ul.menu").slideDown('fast').show(); 
	
		        // Check to see if the menu exceeds the width of the window.
		        var submenu = $(this).parent().find("ul.menu");
		        var offset = submenu.offset();
		        if ( offset.left + submenu.width() > $(window).width() )
		        {
			        var dif = offset.left + submenu.width() - $(window).width();
			        submenu.offset({top: offset.top, left: offset.left - dif - 2});
		        }

		        $(this).parent().hover(function() {}, function()
		        {	
			        $(this).parent().find("ul.menu").slideUp('slow'); //When the mouse hovers out of the menu, move it back up
		        });

	        //Following events are applied to the trigger (Hover events for the trigger)
	        }).hover(function() { 
		        $(this).addClass("menu_hover"); //On hover over, add class "menu_hover"
	        }, function(){	//On Hover Out
		        $(this).removeClass("menu_hover"); //On hover out, remove class "menu_hover"
	        });
        },

        onClicked: function(package_name)
        {
	        for ( a = 0; a < this.items.length; a++ )
	        {
		        item = this.items[a];
		        if ( item.package_name == package_name )
		        {
			        hide_dialogs = false;
			        for ( b = 0; b < item.dialogs.length; b++ )
			        {
				        var dialog = $("#" + item.dialogs[b]).parents(".ui-dialog");
				        if ( dialog.is(":visible") ) { hide_dialogs = true; break; }
			        }
			        for ( b = 0; b < item.opened_dialogs.length; b++ )
			        {
				        if ( hide_dialogs ) { $("#" + item.opened_dialogs[b]).dialog("close"); }
				        else { $("#" + item.opened_dialogs[b]).dialog("open"); }
			        }
                    break;
		        }
	        }
	        this.refresh();
        },

        onClose: function(package_name)
        {
	        for ( a = 0; a < this.items.length; a++ )
	        {
		        item = this.items[a];
		        if ( item.package_name == package_name )
		        {
			        taskbar_entry = document.getElementById("jman_taskbar_" + item.package_name);
			        if ( taskbar_entry ) taskbar_entry.parentNode.removeChild(taskbar_entry);
			        for ( b = 0; b < item.dialogs.length; b++ ) $("#" + item.dialogs[b]).dialog("close");
		        }
	        }
        }
    }
}
