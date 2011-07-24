var update = {
    items : function(){
    },
};

var post = {
    id : function(uuid){document.getElementById("post_id").value = uuid;},
};


function init(){
    $.get("init.json",function(data){
        var init = jsonParse(data);
        post.id(init.post_id);
    });
}

init();
