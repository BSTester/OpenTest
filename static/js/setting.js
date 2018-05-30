$(document).ready(function(){
    //添加项目表单验证
    $.validator.addMethod("notNone", function(value, element){
        var re = /^\s+$/g;
        return this.optional(element) || (!re.test(value));
    }, '该字段不能为空');
    $("#form-project").validate({
        rules:{
            project:{
                required:true,
                notNone:true
            }
        },
        messages:{
            project:{
                required:"项目名称不能为空",
                notNone:"项目名称不能为空"
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
    //禁用启用项目操作
    $(".btn-enable").click(function(){
        var $form = $("form"),
            url = $form.attr("action") + "/update",
            $this_btn = $(this),
            pid = $this_btn.attr("data-pid"),
            status = $this_btn.attr("data-status");
        if(status == 0){
            $("#alert-warning #alert-msg").html("确定要禁用此项目吗?");
            $("#alert-warning").modal();
            $("#alert-ok").unbind().click(function(){
                $.post(url, {"pid": pid, "status": status}, function(data){
                    if(!data.result){
                        $("#tips-warning #tips-msg").html(data.msg);
                        $("#tips-warning").modal();
                    }else{
                        $this_btn.removeClass("btn-danger").addClass("btn-info").attr("data-status",1).text("启用");
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
        }else{
            $.post(url, {"pid": pid, "status": status}, function(data){
                if(!data.result){
                    $("#tips-warning #tips-msg").html(data.msg);
                    $("#tips-warning").modal();
                }else{
                    $this_btn.removeClass("btn-info").addClass("btn-danger").attr("data-status",0).text("禁用");
                    location.href = location.href;
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
    //项目成员管理
    $(".project-user").click(function(){
        var url = $("form").attr("action") + "/getuser",
            pid = $(this).attr("data-pid");
        $("#project-user #project-name").text($(this).attr("data-name"));
        $("#project-user #project-id").attr("value",pid);
        $.post(url, {"pid":pid}, function(data){
            $("#project-user #project-add-user option").remove();
            $("#project-user #project-cur-user option").remove();
            $("#project-user #send-mail input").remove();
            if(data.result){
                var user = data.user,
                    cur_user = data.cur_user;
                for(var i in user){
                    $("#project-user #project-add-user").append("<option class='select-user' value='" + user[i].uid + "'>" + user[i].email + "</option>");
                    $("#project-user .select-user").unbind().dblclick(function(){
                        var uid = $(this).val(),
                            email = $(this).text();
                        $(this).remove();
                        $("#project-user #project-cur-user").append("<option class='remove-user' value='" + uid + "'>" + email + "</option>");
                        $("#project-user #send-mail").append('<input id="mail_' + uid + '" class="checkbox" type="checkbox">');
                        dblbind("#project-user #project-cur-user option[value=" + uid + "]", uid, email, "remove");
                    });
                }
                for(var i in cur_user){
                    $("#project-user #project-cur-user").append("<option class='remove-user' value='" + cur_user[i].uid + "'>" + cur_user[i].email + "</option>");
                    if(cur_user[i].mail){
                        $("#project-user #send-mail").append('<input class="checkbox" id="mail_' + cur_user[i].uid + '" type="checkbox" checked>');
                    }else{
                        $("#project-user #send-mail").append('<input class="checkbox" id="mail_' + cur_user[i].uid + '" type="checkbox">');
                    }
                    $("#project-user .remove-user").unbind().dblclick(function(){
                        var uid = $(this).val(),
                            email = $(this).text();
                        $(this).remove();
                        $("#project-user #send-mail input#mail_" + uid).remove();
                        $("#project-user #project-add-user").append("<option class='select-user' value='" + uid + "'>" + email + "</option>");
                        dblbind("#project-user #project-add-user option[value=" + uid + "]", uid, email, "select");
                    });
                }
                function dblbind(ele, uid, email, op){
                    if(op == 'select'){
                        $(ele).unbind().dblclick(function(){
                            $(this).remove();
                            $("#project-user #project-cur-user").append("<option class='remove-user' value='" + uid + "'>" + email + "</option>");
                            $("#project-user #send-mail").append('<input class="checkbox" id="mail_' + uid + '" type="checkbox">');
                            dblbind("#project-user #project-cur-user option[value=" + uid + "]", uid, email, "remove");
                        });
                    }else{
                        $(ele).unbind().dblclick(function(){
                            $(this).remove();
                            $("#project-user #send-mail input#mail_" + uid).remove();
                            $("#project-user #project-add-user").append("<option class='select-user' value='" + uid + "'>" + email + "</option>");
                            dblbind("#project-user #project-add-user option[value=" + uid + "]", uid, email, "select");
                        });
                    }
                }
                $("#project-user #submit-btn").unbind().click(function(){
                    var $form = $("#project-user form"),
                        url = $form.attr("action"),
                        users = '', uid = '', mail='';
                    $("#project-user #project-cur-user option").each(function(){
                        uid = $(this).attr("value");
                        mail = $("#project-user #send-mail input#mail_" + uid).is(":checked");
                        users = users + '&project_users=' + uid + '&mail=' + mail;
                    });
                    $.post(url, "project_id=" + pid + users, function(data){
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
            }else{
                $("#project-user #project-add-user").append("<option>" + data.msg + "</option>");
            }
        }).error(function(data){
            if(data.status == 403){
                $("#tips-error #tips-error-msg").html("登录超时, 请重新登录!");
                $("#tips-error").modal();
                return
            }
        });
        $("#project-user").modal();
    });
    //项目自定义参数配置
    $(".project-param").click(function(){
        var url = '/admin/setting/project/getparam',
            pid = $(this).attr("data-pid"),
            project = $(this).attr("data-name");
        $.post(url, {"pid": pid}, function(data){
            if(data.result){
                var html = '<div class="form-group">'
                         + '   <label class="col-md-2 control-label">所属项目</label>'
                         + '   <div class="col-md-4">'
                         + '       <label class="control-label project-name"></label>'
                         + '       <input type="hidden" name="project_id">'
                         + '   </div>'
                         + '</div>';
                for(var i in data.msg){
                    html += '<div class="form-group">'
                         + '    <label class="control-label col-md-2">变量类型</label>'
                         + '    <div class="col-md-2">'
                         + '        <select name="type" class="form-control">';
                    if(data.msg[i]['type'] == 'String'){
                        html += '            <option selected>String</option><option>Function</option><option>Data</option>';
                    }else if(data.msg[i]['type'] == 'Function'){
                        html += '            <option>String</option><option selected>Function</option><option>Data</option>';
                    }else{
                        html += '            <option>String</option><option>Function</option><option selected>Data</option>';
                    }
                    html += '        </select>'
                         + '    </div>'
                         + '    <div class="col-md-2">'
                         + '        <input type="text" name="name" class="form-control" value="' + data.msg[i]['name'] + '" placeholder="变量名">'
                         + '    </div>'
                         + '    <div class="col-md-4">';
                    if(data.msg[i]['type'] == 'String'){
                        html += '        <input type="text" name="value" class="form-control" value="' + data.msg[i]['value'] + '" placeholder="变量值">';
                    }else if(data.msg[i]['type'] == 'Function'){
                        $("#project-param div[data-param=Function] option").removeAttr("selected");
                        $("#project-param div[data-param=Function] option[value=" + data.msg[i]['value'] + "]").attr("selected", "selected");
                        var html_temp = $("#project-param div[data-param=Function]").html();
                        html += html_temp;
                    }else{
                        html += '        <textarea name="value" class="form-control" placeholder="变量值">' + data.msg[i]['value'] + '</textarea>';
                    }
                    html += '    </div>'
                         + '    <div class="col-md-1">'
                         + '        <span class="control-label glyphicon ';
                    if(i == 0){
                        html += 'glyphicon-plus';
                    }else{
                        html += 'glyphicon-minus';
                    }
                    html += '" aria-hidden="true"></span>'
                         + '    </div>'
                         + '</div>';
                }
            }else{
                var html = '<div class="form-group">'
                         + '    <label class="col-md-2 control-label">所属项目</label>'
                         + '    <div class="col-md-4">'
                         + '        <label class="control-label project-name"></label>'
                         + '        <input type="hidden" name="project_id">'
                         + '    </div>'
                         + '</div>'
                         + '<div class="form-group">'
                         + '    <label class="control-label col-md-2">变量类型</label>'
                         + '    <div class="col-md-2">'
                         + '        <select name="type" class="form-control">'
                         + '            <option selected>String</option>'
                         + '            <option>Function</option>'
                         + '            <option>Data</option>'
                         + '        </select>'
                         + '    </div>'
                         + '    <div class="col-md-2">'
                         + '        <input type="text" name="name" class="form-control" placeholder="变量名">'
                         + '    </div>'
                         + '    <div class="col-md-4">'
                         + '        <input type="text" name="value" class="form-control" placeholder="变量值">'
                         + '    </div>'
                         + '    <div class="col-md-1">'
                         + '        <span class="control-label glyphicon glyphicon-plus" aria-hidden="true"></span>'
                         + '    </div>'
                         + '</div>';
            }
            $("#project-param .modal-body").html(html);
        }).complete(function(){
            $("#project-param #msg").addClass('sr-only');
            $("#project-param .project-name").text(project);
            $("#project-param input[name=project_id]").val(pid);
            $("#project-param .modal-body .glyphicon-plus").unbind().click(function(){
                var html = '<div class="form-group">'
                         + '    <label class="control-label col-md-2">变量类型</label>'
                         + '    <div class="col-md-2">'
                         + '        <select name="type" class="form-control">'
                         + '            <option selected>String</option>'
                         + '            <option>Function</option>'
                         + '            <option>Data</option>'
                         + '        </select>'
                         + '    </div>'
                         + '    <div class="col-md-2">'
                         + '        <input type="text" name="name" class="form-control" placeholder="变量名">'
                         + '    </div>'
                         + '    <div class="col-md-4">'
                         + '        <input type="text" name="value" class="form-control" placeholder="变量值">'
                         + '    </div>'
                         + '    <div class="col-md-1">'
                         + '        <span class="control-label glyphicon glyphicon-minus" aria-hidden="true"></span>'
                         + '    </div>'
                         + '</div>';
                $("#project-param .modal-body").append(html);
                $("#project-param .modal-body .glyphicon-minus").unbind().click(function(){
                    $(this).parent().parent().remove();
                });
                $("#project-param .modal-body select[name=type]").unbind().change(function(){
                    var value = $(this).val();
                    if(value == 'Function'){
                        $("#project-param div[data-param=Function] option").removeAttr("selected");
                        $("#project-param div[data-param=Function] option[1]").attr("selected", "selected");
                        var html = $("#project-param div[data-param=Function]").html();
                        $(this).parent().siblings(".col-md-4").html(html);
                    }else if(value == 'String'){
                        var html = '        <input type="text" name="value" class="form-control" required placeholder="变量值">';
                        $(this).parent().siblings(".col-md-4").html(html);
                    }else{
                        var html = '        <textarea name="value" class="form-control" required placeholder="变量值">mysql=\r\nuser=\r\npassword=\r\ndatabase=\r\nsql=</textarea>';
                        $(this).parent().siblings(".col-md-4").html(html);
                    }
                });
            });
            $("#project-param .modal-body .glyphicon-minus").unbind().click(function(){
                $(this).parent().parent().remove();
            });
            $("#project-param .modal-body select[name=type]").unbind().change(function(){
                var value = $(this).val();
                if(value == 'Function'){
                    $("#project-param div[data-param=Function] option").removeAttr("selected");
                    $("#project-param div[data-param=Function] option[1]").attr("selected", "selected");
                    var html = $("#project-param div[data-param=Function]").html();
                    $(this).parent().siblings(".col-md-4").html(html);
                }else if(value == 'String'){
                    var html = '        <input type="text" name="value" class="form-control" required placeholder="变量值">';
                    $(this).parent().siblings(".col-md-4").html(html);
                }else{
                    var html = '        <textarea name="value" class="form-control" required placeholder="变量值">mysql=\r\nuser=\r\npassword=\r\ndatabase=\r\nsql=</textarea>';
                    $(this).parent().siblings(".col-md-4").html(html);
                }
            });
            $("#project-param #param-submit-btn").unbind().click(function(){
                var $form = $("#project-param form"),
                    url = $form.attr("action");
                $("#project-param #msg").html('参数合法性校验中……').removeClass('sr-only');
                $.post(url, $form.serialize(), function(data){
                    if(data.result){
                        $("#project-param").modal("hide");
                    }else{
                        $("#project-param #msg").html(data.msg).removeClass('sr-only');
                    }
                }).error(function(data){
                    if(data.status == 403){
                        $("#tips-error #tips-error-msg").html("登录超时, 请重新登录!");
                        $("#tips-error").modal();
                    }
                });
            });
        }).error(function(data){
            if(data.status == 403){
                $("#tips-error #tips-error-msg").html("登录超时, 请重新登录!");
                $("#tips-error").modal();
                return
            }
        });
        $("#project-param").modal();
    });
    //通用新增配置操作
    $("#setting-form #submit").click(function(){
        var $form = $("#setting-form"),
            url = $form.attr("action");
        $.post(url, $form.serialize(), function(data){
            if(!data.result){
                $("#msg").html(data.msg).removeClass('sr-only');
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
    //禁用启用Host设置操作
    $(".btn-enable-set").click(function(){
        var $form = $("form"),
            url = $form.attr("action") + "/update",
            $this_btn = $(this),
            sid = $this_btn.attr("data-sid"),
            pid = $this_btn.attr("data-pid"),
            host = $this_btn.attr("data-host"),
            status = $this_btn.attr("data-status");
        if(status == 0){
            $("#alert-warning #alert-msg").html("确定要禁用此Host吗?");
            $("#alert-warning").modal();
            $("#alert-ok").unbind().click(function(){
                $.post(url, {"pid": pid, "sid": sid, "status": status, "host": host}, function(data){
                    if(!data.result){
                        $("#tips-warning #tips-msg").html(data.msg);
                        $("#tips-warning").modal();
                    }else{
                        $this_btn.removeClass("btn-danger").addClass("btn-info").attr("data-status",1).text("启用");
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
        }else{
            $.post(url, {"pid": pid, "sid": sid, "status": status, "host": host}, function(data){
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
        }
    });
    //接口配置操作
    $(".btn-add-check").click(function(){
        var url = '/admin/setting/interface/getparams',
            sid = $(this).attr("data-id"),
            project = $(this).attr("data-project");
        $.post(url, {"sid": sid}, function(data){
            $("#interface-key .modal-footer #tip-msg").addClass("sr-only");
            if(data.result){
                $("#interface-key form [name=keys]").val(data.msg['key']);
                $("#interface-key form [name=request_headers]").val(data.msg['request_headers']);
                $("#interface-key form [name=request_body]").val(data.msg['request_body']);
            }else{
                $("#interface-key .modal-footer #tip-msg").text(data.msg);
                $("#interface-key .modal-footer #tip-msg").removeClass("sr-only");
            }
        }).complete(function(){
            $("#interface-key form label.project-name").text(project);
            $("#interface-key form input[name=sid]").val(sid);
            $("#interface-key #keys-submit-btn").unbind().click(function(){
                var $form = $("#interface-key form"),
                    url = $form.attr("action");
                $.post(url, $form.serialize(), function(data){
                    if(data.result){
                        $("#interface-key").modal("hide");
                    }else{
                        $("#interface-key .modal-footer #tip-msg").text(data.msg);
                        $("#interface-key .modal-footer #tip-msg").removeClass("sr-only");
                    }
                }).error(function(data){
                    if(data.status == 403){
                        $("#tips-error #tips-error-msg").html("登录超时, 请重新登录!");
                        $("#tips-error").modal();
                        return
                    }
                });
            });
        }).error(function(data){
            if(data.status == 403){
                $("#tips-error #tips-error-msg").html("登录超时, 请重新登录!");
                $("#tips-error").modal();
                return
            }
        });
        $("#interface-key").modal();
    });
    //编辑接口描述
    $("#setting-form td.inter-detail").dblclick(function(){
        $(this).find("textarea:disabled").attr("disabled", false).change(function(){
            var url = $("#setting-form").attr("action") + '/edit',
                sid = $(this).attr("data-sid"),
                detail = $(this).val();
            $.post(url, {"sid": sid, "detail": detail}, function(data){
                if(!data.result){
                    $("#tips-warning #tips-msg").html(data.msg);
                    $("#tips-warning").modal();
                }
            }).error(function(data){
                if(data.status == 403){
                    $("#tips-error #tips-error-msg").html("登录超时, 请重新登录!");
                    $("#tips-error").modal();
                    return
                }
            });
            $(this).attr("disabled", true);
        });
    });
    //设置列表筛选项目
    $(".table-responsive #setting-list").change(function(){
        location.href = '/admin/setting/' + $(this).attr("data-op") + '/' + $(this).val();
    });
});