$('#configmanager_main').dialog({
	autoOpen: false, 
	minWidth: 550,
	minHeight: 300
});

var configmanager = {
    tree: function(path_list, value_list, file_list)
    {
        var html = "";
        var table = {};
        for(var a = 0; a < path_list.length; a++)
        {
            path = path_list[a];
            value = value_list[a];
            file = file_list[a];
            args = path.split("/");

            if ( !table[args[0]] ) table[args[0]] = {}
            var pos = table[args[0]];

            if ( args.length > 1 )
            {
                for(var b = 1; b < args.length; b++)
                {
                    arg = args[b];
                    if ( !pos[arg] ) pos[arg] = {};
                    pos = pos[arg];
                }
            }
            pos["_value"] = value;
            pos["_path"] = path;
            pos["_file"] = file;
        }
        mt.html("configmanager_tree", this.tableToHTML(table), false);
        $("#configmanager_tree").treeview({collapsed: true});
    },

    tableToHTML: function(table)
    {
        var html = "";
        for(var item_name in table)
        {
            var item = table[item_name];
            if (( item["_value"] ) || ( item["_path"] ) || ( item["_file"] ))
            {
                html += "<li href='#' onclick='configmanager.edit(\"" + item["_path"] + "\", \"" + item["_value"] + "\", \"" + item["_file"] + "\")'>" + item_name + "</li>";
            } else {
                html += "<li>" + item_name;
                html += "<ul>" + this.tableToHTML(item) + "</ul>";
                html += "</li>";
            }
        }
        return html;
    },

    edit: function(path, value, file)
    {
        mt.value("configmanager_edit_path", path);
        mt.value("configmanager_edit_value", value);
        mt.value("configmanager_edit_file", file);
    },

    save: function()
    {
        mt("configmanager.save('" + mt.value("configmanager_edit_path") + "', '" + mt.value("configmanager_edit_value") + "', '" + mt.value("configmanager_edit_file") + "')");
    }
};
