$('#confedit_main').dialog({
	autoOpen: false, 
	minWidth: 550,
	minHeight: 300
});

var confedit = {
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
        mt.html("confedit_tree", this.tableToHTML(table), false);
        $("#confedit_tree").treeview({collapsed: true});
    },

    tableToHTML: function(table)
    {
        var html = "";
        for(var item_name in table)
        {
            var item = table[item_name];
            if (( item["_value"] ) || ( item["_path"] ) || ( item["_file"] ))
            {
                html += "<li href='#' onclick='confedit.edit(\"" + item["_path"] + "\", \"" + item["_value"] + "\", \"" + item["_file"] + "\")'>" + item_name + "</li>";
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
        mt.value("confedit_edit_path", path);
        mt.value("confedit_edit_value", value);
        mt.value("confedit_edit_file", file);
    },

    save: function()
    {
        mt("confedit.save('" + mt.value("confedit_edit_path") + "', '" + mt.value("confedit_edit_value") + "', '" + mt.value("confedit_edit_file") + "')");
    }
};
