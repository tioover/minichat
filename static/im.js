var update = {
    items : function(){
        $.get("items.json",function(data){
            var items = jsonParse(data);
        })
    },
};

var post = {
    id : function(){
        $.get("id.json",function(data){
            var post_id = jsonParse(data);
            document.getElementById("post_id").value = post_id;
        })
    },
};
