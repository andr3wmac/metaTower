// Woo jman.

$(document).ready(function() {
    // This chunk of code creates the top boundary for the bar, stops windows from being dragged there.
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

    // Triggered when a dialog is opened.
    var open = $.ui.dialog.prototype.open;
    $.ui.dialog.prototype.open = function() {
        open.apply(this);
        jman.taskbar.onOpenDialog(this.element[0].id);
    };

    // Triggered when a dialog is closed.
    var close = $.ui.dialog.prototype.close;
    $.ui.dialog.prototype.close = function() {
        close.apply(this);
        jman.taskbar.onCloseDialog(this.element[0].id);
    };
});

// These just override some metaTower.js functions with a better jQuery version.
mt.html = function(targetID, data, append)
{
    var target = null;
    if ( targetID == "body" ) target = $("body");
    else target = $("#" + targetID);

    if ( append ) target.append(data);
    else 
    {
        var targ_html = target.html();
        if ( targ_html.toLowerCase() != data.toLowerCase() ) 
        { 
            target.html(data); 
        }
    }
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
    // Just a simple dialog function to shorten things up.
    dialog: function(dname)
    {
        $("#" + dname).dialog("open");
    },

    // Called after all the menu items have been loaded.
    finishedLoading: function()
    {
        var menuElement = document.getElementById("jman_taskbar_main");
        menuElement.style.background = "url(jman/images/tower.png) no-repeat center 1px";
    },

    // Notification engine
    notify: function(text, icon)
    {
        if ( this._nTimeout ) this.hideNotify();

        var html = "";
        if ( !icon || icon === "notice" )
        {
            //html += "<span class='ui-icon ui-icon-notice' style='float:left; margin-right: 7px;'></span>";
            html += text;
        }
        else if ( icon === "error" )
        {
            //html += "<span class='ui-icon ui-icon-alert' style='float:left; margin-right: 7px;'></span>";
            html += "<font color='red'>" + text + "</font>";
        }
        
        mt.html("jman_notify_text", html);

        $("#jman_notify_box").slideToggle('medium');
        this._nTimeout = setTimeout("jman.hideNotify()", 5000);
    },
    hideNotify: function()
    {
        $("#jman_notify_box").slideToggle('fast');
        clearTimeout(this._nTimeout);
        this._nTimeout = null;
    },

    // Contains all menu related functions.
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
            if ( onClick == "" ) onClick = "jman.menu.onClick('" + package_name + "');";
            entry.onClick = onClick;
            this.items.push(entry);

            mt.html("jman_taskbar_main_contents", "<li><a onClick=\"" + entry.onClick + "\" href=\"#\">" + entry.caption + "</a></li>", true);
            jman.taskbar.refresh();
        },

        onClick: function(package_name)
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

    // Taskbar related functions.
    taskbar: {
        items: [],
        TaskbarItem: function()
        {
            this.package_name = "";
            this.caption = "";
            this.dialogs = [];
            this.context = {};

            this.open_dialogs = [];
            this.hidden = false;
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

        find: function(package_name, dialog_name)
        {
            for ( a = 0; a < this.items.length; a++ )
            {
                item = this.items[a];

                package_match = false;
                dialog_match = false;

                if (( package_name == null ) || ( item.package_name == package_name ))
                    package_match = true;
                
                if (( dialog_name == null ) || ( $.inArray(dialog_name, item.dialogs) >= 0 ))
                    dialog_match = true;

                if (package_match && dialog_match) return item;
            }
        },

        // When you add a new item to a div in jquery, it gets pissed. Need to refresh the events.
        refresh: function()
        {
            // ul.jman_taskbar li span
            $("span.menu_trigger").click(function() { //When trigger is clicked...
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
            }, function(){    //On Hover Out
                $(this).removeClass("menu_hover"); //On hover out, remove class "menu_hover"
            });
        },

        onOpenDialog: function(id)
        {
            item = this.find(null, id);
            if ( !item ) return;

            // keeps track of open dialogs.
            if ( $.inArray(id, item.open_dialogs) < 0 ) item.open_dialogs.push(id);

            taskbar_entry = document.getElementById("jman_taskbar_" + item.package_name);
            if ( taskbar_entry == null )
            {
                // taskbar entry html.
                entry_html = "<li style='z-index: 2000' id='jman_taskbar_" + item.package_name;
                entry_html += "'><a href='#' onClick='jman.taskbar.onClick(\"" +item.package_name + "\")'>";
                entry_html += item.caption + "</a><span class='menu_trigger'></span><ul class='menu' style='display: none;'>";
        
                // context menus.
                for ( var caption in item.context )
                {
                    entry_html += "<li><a href='#' onClick='" + item.context[caption] + "'>" + caption + "</a></li>"
                }
                entry_html += "<li><a href='#' onClick='jman.taskbar.onContextClose(\"" + item.package_name + "\")'>Close</a></li>"
                entry_html += "</ul></li><li>"

                // output html and refresh.
                mt.html("jman_taskbar_contents", entry_html, true);
                this.refresh();

                taskbar_entry = document.getElementById("jman_taskbar_" + item.package_name);
            }
            if ( taskbar_entry )
            {
                taskbar_entry.style.opacity = "1.0";
                taskbar_entry.style.fontWeight = "bold";
            }
        },

        onCloseDialog: function(id)
        {
            item = this.find(null, id);
            if ( !item ) return;
            if ( item.hidden ) return; // no nee

            // remove the dialog from the open_dialog array.
            item.open_dialogs = mt.removeValueFromArray(item.open_dialogs, id);

            // if theres no open dialogs, remove from taskbar.
            if ( item.open_dialogs.length == 0 )
            {
                taskbar_entry = document.getElementById("jman_taskbar_" + item.package_name);
                if ( taskbar_entry ) taskbar_entry.parentNode.removeChild(taskbar_entry);
            }
        },

        // When someone clicks the taskbar entry.
        onClick: function(package_name)
        {
            item = this.find(package_name);
            if ( !item ) return;

            if ( item.hidden )
            {
                item.hidden = false;
                for ( a = 0; a < item.open_dialogs.length; a++)
                {
                    dialog = item.open_dialogs[a];
                    $("#" + dialog).dialog("open");
                }
                
            } else {
                item.hidden = true;
                for ( a = 0; a < item.open_dialogs.length; a++)
                {
                    dialog = item.open_dialogs[a];
                    $("#" + dialog).dialog("close");
                }
                taskbar_entry = document.getElementById("jman_taskbar_" + item.package_name);
                if ( taskbar_entry )
                {
                    taskbar_entry.style.opacity = "0.6";
                    taskbar_entry.style.fontWeight = "normal";
                }
            }
        },

        // When the Close button is pressed in the context menu.
        onContextClose: function(package_name)
        {
            item = this.find(package_name);
            if ( !item ) return;

            taskbar_entry = document.getElementById("jman_taskbar_" + item.package_name);
            if ( taskbar_entry ) taskbar_entry.parentNode.removeChild(taskbar_entry);
            for ( b = 0; b < item.dialogs.length; b++ ) $("#" + item.dialogs[b]).dialog("close");
        }
    }
}
