var Update = {
    items : function(){
        $.get("items.json",function(data){
            $("#list").html("");
            var items = jsonParse(data);
            //This used jQuery template.
            $( "#itemsTemplate" ).tmpl(items).appendTo( "#list" );
            $(".item").show();
            Update.comet(items[0].id);
        });
    },

    comet : function(sence){
        $.get("comet.json",{sence:sence},function(data){
            var items = jsonParse(data);
            $( "#itemsTemplate" ).tmpl(items).prependTo( "#list" );
            $(".item").slideDown(500);
            Update.comet(items[0].id);
        });
    },
};


var Post = {
    start : function(){
        if ($("#name").val() == ""){$("#name").focus();}
        else if ($("#content").val() == ""){$("#content").focus();}
        else {
            Post.post();
        }
    },

    post : function(){
        var post_data = {
            name : $("#name").val(),
            content : $("#content").val(),
            email : $("#email").val(),
        }
        $.post("add/",post_data,function(){
            $("#content").val("");
        });
    },
};

var Cookie = {
}

var Style = {
    start : function(){
        Style.masonry();
    },
    masonry : function(){
        $('#list').masonry({
            itemSelector : '.item',
            columnWidth : 240
        });
    },
};


$(document).ready(function(){
    Update.items(); //ajax load all item.
    Style.start();
    $("#post").click(function(e){
        e.preventDefault();//stop default event.
        Post.start();//ajax post.
    });
});
