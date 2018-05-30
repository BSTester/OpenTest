$(document).ready(function(){
    $("[data-toggle=popover]").popover();
    //通用删除操作
    $(".btn-delete").click(function(){
        var $form = $("form"),
            url = $form.attr("action") + "/delete",
            id = $(this).attr("data-id");
        $("#alert-warning #alert-msg").html("确定要删除此项吗?");
        $("#alert-warning").modal();
        $("#alert-ok").unbind().click(function(){
            $.post(url, {"id":id}, function(data){
                if(!data.result){
                    $("#tips-warning #tips-msg").html(data.msg);
                    $("#tips-warning").modal();
                }else{
                    location.href = location.href;
                }
            }).error(function(data){
                if(data.status == 403){
                    $("#tips-error #tips-error-msg").html("登录超时, 请重新登录!");
                    $("#tips-error").modal();
                    return
                }
            });
        });
    });
    //筛选导航每页显示数目
    $(".pagination #page-limit").change(function(){
        location.href = $(".page-nav .pagination .active a").attr("data-nav") + '/' + $(this).val();
    });
    $(".pagination #go-to").change(function(){
        var page = $(this).val();
        if($.isNumeric(page) && page > 0){
            location.href = $(this).attr("data-nav") + '/' + page + '/' + $(".pagination #page-limit").val();
        }else{
            $(this).val("");
        }
    });
});