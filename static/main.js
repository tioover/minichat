function main(){
    item.update(0); //ajax load all item.
    $("#post").click(function(e){
        e.preventDefault();//stop default event.
        item.post();//ajax post.
    });
}

$(document).ready(function(){
    main();
});

var item = {
    "update": function(sence){
        //长轮询加载item
        var data = {sence:sence};
        if (sence == 0) data={}
        $.get("items.json",data,function(json_str){
            var items = JSON.parse(json_str);
            show.template_update(items);
            item.update(items[0].id); //递归调用，进行下一次长轮询
        });
    },

    "post": function(){
        //ajax发送内容
        if (show.check()){
            var post_data = {
                name : $("#name").val(),
                content : $("#content").val(),
                email : $("#email").val(),
            }
            $.post("add/",post_data,function(){
                $("#content").val(""); //清空输入框
            });
        }
    },
}

var show = {
    "check": function(){
        //检查表单是否填写完整
        if ($("#name").val() == "") $("#name").focus();
        else if ($("#email").val() == "") $("email").focus();
        else if ($("#content").val() == "") $("#content").focus();
        else return true
    },
    
    "template_update": function(items){
        //使用jQuery template来更新HTML,模板内容见../template/home.html 头部.
        $("#itemsTemplate").tmpl(items).prependTo("#list");
        $(".item").slideDown();
    },
}
