function items (sence){
    if (sence == 0) var sence = {};
    else sence = {sence:sence};
    $.get("items.json",sence,function(data){
        var items = jsonParse(data);
        //This used jQuery template.
        $( "#itemsTemplate" ).tmpl(items).prependTo( "#list" );
        $(".item").slideDown(500);
        items(items[0].id);
    });
}

function post(){
    if ($("#name").val() == ""){$("#name").focus();}
    else if ($("#content").val() == ""){$("#content").focus();}
    else {
        var post_data = {
            name : $("#name").val(),
            content : $("#content").val(),
            email : $("#email").val(),
        }
        $.post("add/",post_data,function(){
            $("#content").val("");
        });
    }
}

function chat(){
    $("#tit").click(function(){
        $("#chatform").slideToggle();
    });
}

function masonry(){
    $('#list').masonry({
        itemSelector : '.item',
        columnWidth : 240
    });
}


$(document).ready(function(){
    items(0); //ajax load all item.
    masonry();
    chat();
    $("#post").click(function(e){
        e.preventDefault();//stop default event.
        post();//ajax post.
    });
});
