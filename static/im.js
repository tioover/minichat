var Update = {
    items : function(){
        $.get("items.json",function(data){
            var items = jsonParse(data);
            //This used jQuery template.
            $( "#itemsTemplate" ).tmpl(items).appendTo( "#list" );
        });
    },
};


var Post = {
    start : function(){
        Notice.posting();
        Post.id();
    },

    id : function(){ 
        //A unique ID to action to prevent repeat POST.
        $.get("post_id.json",function(data){
            var uuid = jsonParse(data);
            document.getElementById("post_id").value = uuid;
            Post.post();
        });
    },

    post : function(){
        var post_data = "name=" + $("#name").val() + "&" + 
                        "email=" + $("#email").val() + "&" +
                        "content=" + $("#content").val() + "&" +
                        "post_id=" + $("#post_id").val() + "&";
        $.post("add/",post_data,function(data){
            var result = jsonParse(data);
            if (result == "success") {
                Notice.post_success();
            }
            else if (result == "failure") {
                Notice.post_failure();
            }
            else {
                Notice.post_other_failure();
            }
        });
    },
};


var Notice = {
    post_success : function(){alert("成功！");},

    post_failure : function(){alert("失败……");},

    post_other_error : function(){alert("未知错误");},

    posting : function(){},
};


function main(){
    Update.items(); //ajax load all item.
    Post.id();
    $("#post").click(function(e){
        e.preventDefault();//stop default event.
        Post.start();//ajax post.
    });
}

$(document).ready(function(){
    main();
});
