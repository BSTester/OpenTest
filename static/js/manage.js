$(document).ready(function(){
    //保存配置
    $("#submit").click(function(){
        var $form = $("form"),
            url = $form.attr("action");
        $("#msg").addClass('sr-only');
        $.post(url, $form.serialize(), function(data){
            $("#msg").html(data.msg).removeClass('sr-only');
        }).error(function(data){
            if(data.status == 403){
                $("#tips-error #tips-error-msg").html("登录超时, 请重新登录!");
                $("#tips-error").modal();
                return
            }
        });
    });
    //邮件配置测试
    $("#mail-test").click(function(){
        var $form = $("form"),
            url = $form.attr("action") + '/test';
        $("#test-msg").html('测试中, 请稍等片刻……').removeClass('sr-only');
        $.post(url, $form.serialize(), function(data){
            $("#test-msg").html(data.msg).removeClass('sr-only');
        }).error(function(data){
            if(data.status == 403){
                $("#tips-error #tips-error-msg").html("登录超时, 请重新登录!");
                $("#tips-error").modal();
                return
            }
        });
    });
    //禁用启用用户操作
    $(".btn-enable-user").click(function(){
        var url = "/admin/manage/users/status",
            $this_btn = $(this),
            id = $this_btn.attr("data-id"),
            status = $this_btn.attr("data-status");
        if(status == 0){
            $("#alert-warning #alert-msg").html("确定要禁用此项目吗?");
            $("#alert-warning").modal();
            $("#alert-ok").unbind().click(function(){
                $.post(url, {"id": id, "status": status}, function(data){
                    if(!data.result){
                        $("#tips-warning #tips-msg").html(data.msg);
                        $("#tips-warning").modal();
                    }else{
                        $this_btn.removeClass("btn-danger").addClass("btn-info").attr("data-status",1).text("启用");
                    }
                }).error(function(data){
                    if(data.status == 403){
                        $("#tips-error #tips-error-msg").html("登录超时, 请重新登录!");
                        $("#tips-error").modal();
                        return
                    }
                });
            });
        }else{
            $.post(url, {"id": id, "status": status}, function(data){
                if(!data.result){
                    $("#tips-warning #tips-msg").html(data.msg);
                    $("#tips-warning").modal();
                }else{
                    $this_btn.removeClass("btn-info").addClass("btn-danger").attr("data-status",0).text("禁用");
                }
            }).error(function(data){
                if(data.status == 403){
                    $("#tips-error #tips-error-msg").html("登录超时, 请重新登录!");
                    $("#tips-error").modal();
                    return
                }
            });
        }
    });
    //设置管理员操作
    $(".btn-enable-role").click(function(){
        var url = "/admin/manage/users/role",
            $this_btn = $(this),
            id = $this_btn.attr("data-id"),
            role = $this_btn.attr("data-role");
        if(role == 1){
            $("#alert-warning #alert-msg").html("确定要将此用户设置为管理员吗?");
            $("#alert-warning").modal();
            $("#alert-ok").unbind().click(function(){
                $.post(url, {"id": id, "role": role}, function(data){
                    if(!data.result){
                        $("#tips-warning #tips-msg").html(data.msg);
                        $("#tips-warning").modal();
                    }else{
                        $this_btn.removeClass("btn-danger").addClass("btn-info").attr("data-role",2).text("取消管理员");
                        $(".data-col-role-" + id).text("管理员");
                    }
                }).error(function(data){
                    if(data.status == 403){
                        $("#tips-error #tips-error-msg").html("登录超时, 请重新登录!");
                        $("#tips-error").modal();
                        return
                    }
                });
            });
        }else if(role == 2){
            $.post(url, {"id": id, "role": role}, function(data){
                if(!data.result){
                    $("#tips-warning #tips-msg").html(data.msg);
                    $("#tips-warning").modal();
                }else{
                    $this_btn.removeClass("btn-info").addClass("btn-danger").attr("data-role",1).text("设为管理员");
                    $(".data-col-role-" + id).text("用户");
                }
            }).error(function(data){
                if(data.status == 403){
                    $("#tips-error #tips-error-msg").html("登录超时, 请重新登录!");
                    $("#tips-error").modal();
                    return
                }
            });
        }
    });
    //重置密码操作
    $(".btn-reset-pwd").click(function(){
        var url = "/admin/manage/users/reset",
            id = $(this).attr("data-id"),
            email = $(this).attr("data-email");
        $("#alert-warning #alert-msg").html("确定要重置用户 " + email + " 的密码为 123456 吗?");
        $("#alert-warning").modal();
        $("#alert-ok").unbind().click(function(){
            $.post(url, {"id": id}, function(data){
                $("#tips-warning #tips-msg").html(data.msg);
                $("#tips-warning").modal();
            }).error(function(data){
                if(data.status == 403){
                    $("#tips-error #tips-error-msg").html("登录超时, 请重新登录!");
                    $("#tips-error").modal();
                    return
                }
            });
        });
    });
    //添加用户表单验证
    $.validator.addMethod("notNone", function(value, element){
        var re = /^\s+$/g;
        return this.optional(element) || (!re.test(value));
    }, '邮箱不能为空');
    $("#form-users").validate({
        rules:{
            email:{
                required:true,
                notNone:true,
                email:true
            }
        },
        messages:{
            email:{
                required:"邮箱不能为空",
                notNone:"邮箱不能为空",
                email:"邮箱格式不正确"
            }
        },
        errorPlacement:function(error, element){
            $(element).popover("destroy");
            $(element).popover({content: error.text()});
            $(element).popover("show");
        },
        success:function(element){
            $(element).popover("destroy");
        }
    });
});