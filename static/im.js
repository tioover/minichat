var model = {
    items : function(){
                    var get = $.get("api/items.json",function(data){
                                    //items = jsonParse(data);
                                    //update.itemlist(items);
                                })
                    return(get)
                    }
};

var update = {
    itemlist : function(){
                    var items = model.items()
                    alert(items.responseText)
                    return(items.status)
               }
};
