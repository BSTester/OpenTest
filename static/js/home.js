$(document).ready(function(){
    $("[data-toggle=popover]").popover();
    //注册表单验证
    $("#form-signup").validate({
        rules:{
            email:{
                required:true,
                email:true
            },
            username:{
                required:true,
                minlength:4
            },
            password:{
                required:true,
                minlength:6,
                maxlength:20
            },
            confirm_password:{
                required:true,
                minlength:6,
                maxlength:20,
                equalTo:"#password"
            }
        },
        messages:{
            email:{
                required:"用户名不能为空",
                email:"请输入正确的电子邮箱地址"
            },
            username:{
                required:"不能为空",
                minlength:"至少4个字符"
            },
            password:{
                required:"密码不能为空",
                maxlength:"请输入6-20位字符组成的密码",
                minlength:"请输入6-20位字符组成的密码"
            },
            confirm_password:{
                required:"确认密码不能为空",
                maxlength:"请输入6-20位字符组成的密码",
                minlength:"请输入6-20位字符组成的密码",
                equalTo:"确认密码与输入的密码不一致"
            }
        },
        errorPlacement:function(error, element){
            $(element).popover("destroy");
            $(element).popover({content: error.text()});
            $(element).popover("show");
        },
        success:function(element){
            $(element).popover("destroy");
            $("#signup-submit").attr("disabled",false);
        }
    });
    //注册操作
    $("#signup-submit").click(function(){
        var $form = $("#form-signup"),
            url = $form.attr("action") + "/check";
            username = $form.find("input[name=username]").val();
        $.post(url, {"username":username}, function(data){
            if(data.result == false){
                $("input[name=username]").popover("destroy");
                $("input[name=username]").popover({content: data.msg});
                $("input[name=username]").popover("show");
            }else{
                $("#form-signup").submit();
            }
        });
    });
    //登录操作
    $("#signin-submit").click(function(){
        var $form = $("#form-signin"),
            url = $form.attr("action");
        $.post(url , $form.serialize(), function(data){
            if(data.result == false){
                if(data.error == 'username'){
                    $("#username").popover("destroy");
                    $("#username").popover({content: data.msg});
                    $("#username").popover("show");
                }else{
                    $("#password").popover("destroy");
                    $("#password").popover({content: data.msg});
                    $("#password").popover("show");
                }
            }else{
                $("#form-signin").submit();
            }
        });
    });
});