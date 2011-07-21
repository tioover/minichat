//document.write("Hello World!");
$.get("api/items.json",function(data){
    var items = jsonParse(data);
    for (i in items) {
        document.write(items[i].content);
        document.write("<br />");
    }
    document.write("<hr />");
    document.write(items[0].content);
});
