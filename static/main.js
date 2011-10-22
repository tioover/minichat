function update(sence){
    //长轮询加载item
    var data = {sence:sence};
    if (sence == 0) data={}
    $.get("items.json",data,function(json_str){
        var items = JSON.parse(json_str);
        template_update(items);
        update(items[0].id); //递归调用，进行下一次长轮询
    });
}

function template_update(items){
    //使用jQuery template来更新HTML,模板内容见../index.html 头部.
    $("#itemsTemplate").tmpl(items).prependTo("#list");
    $(".item").slideDown(500);
}

function post(){
    //ajax发送内容
    if (check()){
        var post_data = {
            name : $("#name").val(),
            content : $("#content").val(),
            email : $("#email").val(),
        }
        $.post("add/",post_data,function(){
            $("#content").val(""); //清空输入框
        });
    }
}

function check(){
    //检查表单是否填写完整
    if ($("#name").val() == "") $("#name").focus();
    else if ($("#email").val() == "") $("email").focus();
    else if ($("#content").val() == "") $("#content").focus();
    else return true
}

function main(){
    update(0); //ajax load all item.
    $("#post").click(function(e){
        e.preventDefault();//stop default event.
        post();//ajax post.
    });
}

$(document).ready(function(){
    main();
});
