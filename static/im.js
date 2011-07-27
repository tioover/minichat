var Update = {
    items : function(){
        $.get("items.json",function(data){
            $("#list").html("");
            var items = jsonParse(data);
            //This used jQuery template.
            $( "#itemsTemplate" ).tmpl(items).appendTo( "#list" );
            Update.comet(items[0].id);
        });
    },

    comet : function(sence){
        $.get("comet.json",{sence:sence},function(data){
            var items = jsonParse(data);
            $( "#itemsTemplate" ).tmpl(items).prependTo( "#list" );
            Update.comet(items[0].id);
        });
    },
};


var Post = {
    start : function(){
        Post.post();
        Notice.posting();
    },

    post : function(){
        var post_data = {
            name : $("#name").val(),
            email : $("#email").val(),
            content : $("#content").val(),
        }
        $.post("add/",post_data,function(){
            Notice.posted();
        });
    },
};


var Notice = {

    posting : function(){},

    posted : function(){},
};


$(document).ready(function(){
    Update.items(); //ajax load all item.
    $("#post").click(function(e){
        e.preventDefault();//stop default event.
        Post.start();//ajax post.
    });
});
