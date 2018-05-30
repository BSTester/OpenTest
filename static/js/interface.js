$(document).ready(function(){
    //获取项目加解密算法操作
    $("#crypt-form #project").change(function(){
        var $form = $("#crypt-form"),
            url = $form.attr("action") + '/getcrypt',
            pid = $(this).val();
        $.post(url, {"project": pid}, function(data){
            if(data.result){
                var crypt = '';
                for(var v in data.msg){
                    crypt += "<option value='" + data.msg[v] + "'>" + data.msg[v] + "</option>";
                }
                $("#crypt").html(crypt);
            }else{
                $("#crypt").html("<option>" + data.msg + "</option>");
            }
        }, "json").error(function(data){
            if(data.status == 403){
                $("#tips-error #tips-error-msg").html("登录超时, 请重新登录!");
                $("#tips-error").modal();
            }else{
                $("#crypt-text").html('服务器异常!');
                return
            }
        });
    });
    //加解密操作
    $("#crypt-form #crypt-submit").click(function(){
        var $form = $("#crypt-form"),
            url = $form.attr("action");
        $.post(url, $form.serialize(), function(data){
            $("#crypt-text").html(data.msg);
        }, "json").error(function(data){
            if(data.status == 403){
                $("#tips-error #tips-error-msg").html("登录超时, 请重新登录!");
                $("#tips-error").modal();
            }else{
                $("#crypt-text").html('服务器异常!');
                return
            }
        });
    });
    //获取项目接口列表
    $("#single-test #project").change(function(){
        var url = '/admin/interface-test/single/gethost',
            pid = $(this).val();
        $.post(url, {"pid": pid}, function(data){
            if(data.result){
                var hosts = "<option value='none' selected>请选择域名</option>";
                for(var i in data.msg){
                    hosts += "<option value='" + data.msg[i] + "'>" + data.msg[i] + "</option>";
                    $("#single-test #host").html(hosts);
                }
            }else{
                if(data.msg.length > 0){
                    $("#single-test #host").html("<option value='none' selected>" + data.msg[0] + "</option>");
                }else{
                    $("#single-test #host").html("<option value='none' selected>请选择域名</option>");
                }
            }
            $("#single-test #host-url").html("<option value='none' selected>请选择接口</option>");
            var encrypt = "<option value='none' selected>不加密</option>";
            if(data.encrypt.length > 0){
                encrypt += "<option value='" + data.encrypt[0] + "' selected>" + data.encrypt[0] + "</option>";
            }
            $("#single-test #body-crypt").html(encrypt);
            $("#single-test #env").html("<option value='none'>默认环境</option>");
        }).error(function(data){
            if(data.status == 403){
                $("#tips-error #tips-error-msg").html("登录超时, 请重新登录!");
                $("#tips-error").modal();
                return
            }
        });
    });
    $("#single-test #host").change(function(){
        var url = '/admin/interface-test/single/geturl',
            pid = $("#single-test #project").val(),
            host = $(this).val();
        $.post(url, {"pid": pid, "host": host}, function(data){
            if(data.result){
                var urls = "";
                for(var i in data.msg){
                    urls += "<option data-toggle='tooltip' data-placement='right' title='" + data.msg[i]['label'] + "' value='" + data.msg[i]['path']
                         + "' data-keys='" + data.msg[i]['check_key'] + "' data-headers='" + data.msg[i]['request_headers'] + "' data-body='" + data.msg[i]['request_body'] + "'>" + data.msg[i]['path'] + "</option>";
                }
                var ips = "<option value='none'>默认环境</option>";
                for(var i in data.ips){
                    if(data.ips[i]['status'] == 1){
                        ips += "<option selected value='" + data.ips[i]['ip'] + "'>" + data.ips[i]['ip'] + "</option>";
                    }else{
                        ips += "<option value='" + data.ips[i]['ip'] + "'>" + data.ips[i]['ip'] + "</option>";
                    }
                }
                $("#single-test #env").html(ips);
                $("#single-test #host-url").html(urls);
            }else{
                if(data.msg.length > 0){
                    $("#single-test #host-url").html("<option value='none' selected>" + data.msg + "</option>");
                }else{
                    $("#single-test #host-url").html("<option value='none' selected>请选择接口</option>");
                    $("#single-test #env").html("<option value='none'>默认环境</option>");
                }
            }
        }).complete(function(){
            var headers = $("#single-test #host-url").find("option:selected").attr("data-headers"),
                body = $("#single-test #host-url").find("option:selected").attr("data-body"),
                keys = $("#single-test #host-url").find("option:selected").attr("data-keys"),
                label = $("#single-test #host-url").find("option:selected").attr("title");
            $("#single-test #headers").val(headers);
            $("#single-test #body").val(body);
            $("#single-test #keys").val(keys);
            $("#single-test #url-label").val(label);
        }).error(function(data){
            if(data.status == 403){
                $("#tips-error #tips-error-msg").html("登录超时, 请重新登录!");
                $("#tips-error").modal();
                return
            }
        });
    });
    $("#single-test #host-url").change(function(){
        var headers = $(this).find("option:selected").attr("data-headers"),
            body = $(this).find("option:selected").attr("data-body"),
            keys = $(this).find("option:selected").attr("data-keys"),
            label = $(this).find("option:selected").attr("title");
        $("#single-test #headers").val(headers);
        $("#single-test #body").val(body);
        $("#single-test #keys").val(keys);
        $("#single-test #url-label").val(label);
    });
    //单接口测试操作
    $("#single-test #test-submit").click(function(){
        var $form = $("#single-test"),
            url = $form.attr("action") + '/test';
        $("#single-test #test-response").html('请求接口中, 请在此页面稍等片刻...');
        $.post(url, $form.serialize(), function(data){
            if(data.result){
                if(data.type == 'test'){
                    var html = '<table class="table"><tr><th>请求 Headers: </th><td>';
                    for(var i in data.msg['request_headers']){
                        html += data.msg['request_headers'][i] + '</br>';
                    }
                    html += '</td></tr><tr><th>请求 Body: </th><td>' + data.msg['request_body'] + '</td></tr><tr><th>Status: </th><td>'
                         + data.msg['code'] + ' ' + data.msg['reason'] + '</td></tr>';
                    if(data.msg['error'] != null){
                        html += '<tr><th>Error: </th><td>' + data.msg['error'] + '</td></tr>';
                    }
                    html += '<tr><th>响应 Headers: </th><td>';
                    for(var i in data.msg['headers']){
                        html += data.msg['headers'][i] + '</br>';
                    }
                    html += '</td></tr>';
                    for(var i in data.msg['check_key']){
                        if(i == 0){
                            html += '<tr><th>返回值检查: </th>';
                        }else{
                            html += '<tr><td></td>';
                        }
                        html += '<td>深度: <b>' + data.msg['check_key'][i]['deep'] + '</b><br>字段: <b>['
                             + data.msg['check_key'][i]['keys'] + ']</b><br>结果: <b style="color:#ff0000;">' + data.msg['check_key'][i]['result']['key_result'] + '</b><br>';
                        for(var j in data.msg['check_key'][i]['result']){
                            if(j != 'key_result'){
                                if(data.msg['check_key'][i]['result'][j] == true){
                                    html += '<b>' + j + ': ' + data.msg['check_key'][i]['result'][j] + '</b><br>';
                                }else{
                                    html += '<b style="color:#ff0000;">' + j + ': ' + data.msg['check_key'][i]['result'][j] + '</b><br>';
                                }
                            }
                        }
                        html += '</td></tr>';
                    }
                    if(data.msg['checkpoint'].length > 0){
                        for(var i in data.msg['checkpoint']){
                            if(i == 0){
                                html += '<tr><th>检查点: </th>';
                            }else{
                                html += '<tr><td></td>';
                            }
                            if(data.msg['checkpoint'][i]['checkpoint'] != undefined){
                                html += '<td><b>[' + data.msg['checkpoint'][i]['checkpoint'] + ']</b>, 结果: ';
                                if(data.msg['checkpoint'][i]['result']){
                                    html += '<b>' + data.msg['checkpoint'][i]['result'] + '</b></td></tr>';
                                }else{
                                    html += '<b style="color:#ff0000;">' + data.msg['checkpoint'][i]['result'] + '</b></td></tr>';
                                }
                            }
                        }
                    }
                    var j = 0;
                    for(var i in data.msg['correlation']){
                        if(j == 0){
                            html += '<tr><th>关联参数: </th>';
                        }else{
                            html += '<tr><td></td>';
                        }
                        html += '<td>' + i + '=<b>'+ data.msg['correlation'][i] + '</b></td></tr>';
                        j += 1;
                    }
                    html += '<tr><th>响应 Body: </th><td>' + data.msg['body'] + '</td></tr>';
                    if($("#single-test #body-crypt").val() != "none"){
                        html += '<tr><th>响应 Body(解密后): </th><td>' + data.msg['body_decrypt'] + '</td></tr></table>';
                    }else{
                        html += '</table>';
                    }
                }else{
                    var html = '<table class="table"><tr><th>请求 Body: </th><td>' + data.msg + '</td></tr></table>';
                }
                $("#single-test #test-response").html(html);
            }else{
                $("#single-test #test-response").html(data.msg);
            }
        }).error(function(data){
            if(data.status == 403){
                $("#tips-error #tips-error-msg").html("登录超时, 请重新登录!");
                $("#tips-error").modal();
                return
            }else{
                $("#single-test #test-response").html("服务器异常");
            }
        });
    });
    //配置测试接口参数
    $("#list-add").click(function(){
        var id = $("#single-test #project").siblings("textarea").attr("data-id");
        $("#single-test").trigger("reset");
        $("#single-test #project").html($("#single-test #project").siblings("textarea").val());
        $("#single-test #host").html('<option value="none" selected>请选择域名</option>');
        $("#single-test #host-url").html('<option value="none" selected>请选择接口</option>');
        $("#single-test #env").html('<option value="none">默认环境</option>');
        $("#single-test input[type=hidden]#sid").val("0");
        $("#single-test input[type=hidden]#num-id").val(id);
        $("#single-test #test-response").text("");
        $("#add").modal();
    });
    //保存测试接口参数
    $("#single-test #save-submit").click(function(){
        var $form = $("#single-test"),
            url = $form.attr("action") + '/add';
        $.post(url, $form.serialize(), function(data){
            if(data.result){
                location.href = location.href;
            }else{
                $("#single-test #test-response").text(data.msg);
            }
        }).error(function(data){
            if(data.status == 403){
                $("#tips-error #tips-error-msg").html("登录超时, 请重新登录!");
                $("#tips-error").modal();
                return
            }
        });
    });
    //接口列表筛选项目
    $("#list-form #project-run").change(function(){
        var url = $("#list-form").attr("action"),
            pid = $("#list-form #project-run").val();
        location.href = url + '/' + pid;
    });
    //任务列表筛选项目
    $(".table-responsive #overview-list").change(function(){
        location.href = '/admin/interface-test/overview/' + $(this).val();
    });
    //报告列表筛选项目
    $(".table-responsive #reports-list").change(function(){
        location.href = '/admin/interface-test/reports/' + $(this).val();
    });
    //编辑接口信息
    $(".table-responsive .btn-edit").click(function(){
        var url = $("#list-form").attr("action") + '/edit',
            sid = $(this).attr("data-sid"),
            id = $(this).attr("data-id"),
            pid = $(this).attr("data-pid"),
            project = $(this).attr("data-project");
        $.post(url, {"sid": sid, "pid": pid}, function(data){
            if(data.result){
                var ips = "<option value='none'>默认环境</option>";
                for(var i in data.ips){
                    if(data.ips[i]['status'] == 1){
                        ips += "<option selected value='" + data.ips[i]['ip'] + "'>" + data.ips[i]['ip'] + "</option>";
                    }else{
                        ips += "<option value='" + data.ips[i]['ip'] + "'>" + data.ips[i]['ip'] + "</option>";
                    }
                }
                $("#single-test #env").html(ips);
                $("#single-test #project").html('<option value="' + pid + '" selected>' + project + '</option>');
                $("#single-test #host").html('<option value="' + data.msg['host'] + '" selected>' + data.msg['host'] + '</option>');
                $("#single-test #host-url").html('<option value="' + data.msg['url'] + '" selected>' + data.msg['url'] + '</option>');
                if(data.msg['method'] == 'POST'){
                    $("#single-test #method").html('<option value="' + data.msg['method'] + '" selected>' + data.msg['method'] + '</option><option value="GET">GET</option>');
                }else{
                    $("#single-test #method").html('<option value="' + data.msg['method'] + '" selected>' + data.msg['method'] + '</option><option value="POST">POST</option>');
                }
                $("#single-test #headers").val(data.msg['headers']);
                $("#single-test #body").val(data.msg['body']);
                $("#single-test #keys").val(data.msg['check_key']);
                if(data.msg['crypt'] == 'none'){
                    if(data.msg['encrypt'] == ''){
                        $("#single-test #body-crypt").html('<option value="none">不加密</option>');
                    }else{
                        $("#single-test #body-crypt").html('<option value="none" selected>不加密</option><option value="' + data.msg['encrypt'] + '">' + data.msg['encrypt'] + '</option>');
                    }
                }else{
                    $("#single-test #body-crypt").html('<option value="none">不加密</option><option value="' + data.msg['crypt'] + '" selected>' + data.msg['crypt'] + '</option>');
                }
                $("#single-test #encrypt-content").val(data.msg['encrypt_content']);
                $("#single-test #decrypt-content").val(data.msg['decrypt_content']);
                $("#single-test #checkpoint").val(data.msg['checkpoint']);
                $("#single-test #correlation").val(data.msg['correlation']);
                if(!data.msg['follow_redirects']){
                    $("#single-test input[name=redirects]").prop("checked", false);
                }else{
                    $("#single-test input[name=redirects]").prop("checked", true);
                }
                $("#single-test input[type=hidden]#sid").val(sid);
                $("#single-test input[type=hidden]#num-id").val(id);
                $("#single-test input[type=hidden]#url-label").val(data.msg['label']);
                $("#single-test #comment").val(data.msg['comment']);
                $("#single-test #test-response").text("");
            }else{
                $("#single-test #test-response").text(data.msg);
            }
            $("#add").modal();
        }).error(function(data){
            if(data.status == 403){
                $("#tips-error #tips-error-msg").html("登录超时, 请重新登录!");
                $("#tips-error").modal();
                return
            }
        });
    });
    //添加用例集
    $("#list-form #suite").click(function(){
        var url = $("#list-form").attr("action") + '/add',
            pid = $("#list-form #project-run").val(),
            id = $("#list-form div.moveup:last").attr("data-id"),
            name = $("#list-form #test-suite").val();
        $.post(url, {"pid": pid, "id":id, "name": name}, function(data){
            if(data.result){
                location.href = location.href;
            }else{
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
    });
    //编辑用例描述
    $("#list-form td.case-edit").dblclick(function(){
        $(this).find("textarea:disabled, input:disabled").attr("disabled", false).change(function(){
            var url = $("#list-form").attr("action") + '/edit',
                sid = $(this).attr("data-sid"),
                type = $(this).attr("data-type"),
                value = $(this).val();
            $.post(url, {"sid": sid, "type":type, "value": value}, function(data){
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
    //上移测试接口
    $(".table-responsive .btn-moveup").click(function(){
        var url = $("#list-form").attr("action") + '/up',
            sid = $(this).attr("data-sid"),
            id = $(this).attr("data-id"),
            pre_sid = $(this).parent().parent().prev().find("div.moveup").attr("data-sid"),
            pre_id = $(this).parent().parent().prev().find("div.moveup").attr("data-id");
        $.post(url, {"sid": sid, "id": id, "pre_sid": pre_sid, "pre_id": pre_id}, function(data){
            location.href = location.href;
        }).error(function(data){
            if(data.status == 403){
                $("#tips-error #tips-error-msg").html("登录超时, 请重新登录!");
                $("#tips-error").modal();
                return
            }
        });
    });
    //选择所有测试用例
    $("#list-form #select-all").click(function(){
        if(!$(this).prop("checked")){
            $(this).prop("checked", false);
            $("#list-form .table-responsive input[name=sid]").prop("checked", false);
        }else{
            $(this).prop("checked", true);
            $("#list-form .table-responsive input[name=sid]").prop("checked", true);
        }
    });
    //选择单个测试用例
    $("#list-form .table-responsive input[name=sid]").click(function(){
        if(!$(this).prop("checked")){
            $(this).prop("checked", false);
            $("#list-form #select-all").prop("checked", false);
        }else{
            $(this).prop("checked", true);
        }
        var count = $("#list-form .table-responsive input[name=sid]").length;
        var checked = $("#list-form .table-responsive input[name=sid]:checked").length;
        if(count == checked){
            $("#list-form #select-all").prop("checked", true);
        }
    });
    //查看接口配置详情
    $("#list-form td.detail").click(function(){
        var url = $("#list-form").attr("action") + '/detail',
            sid = $(this).parent().find("div.moveup").attr("data-sid");
        $("div#list-detail").hide("fast", function(){
            $.post(url, {"sid": sid}, function(data){
                if(data.result){
                    $("div#list-detail #url").html(data.msg.url);
                    $("div#list-detail table #test-url").html(data.msg.url);
                    if(data.msg.follow_redirects){
                        $("div#list-detail table #test-follow_redirects").html("是");
                    }else{
                        $("div#list-detail table #test-follow_redirects").html("否");
                    }
                    $("div#list-detail table #test-label").html(data.msg.label);
                    $("div#list-detail table #test-method").html(data.msg.method);
                    var html = "", headers = data.msg.headers.split("\r\n");
                    for(var i in headers){
                        html += headers[i] + "<br>";
                    }
                    $("div#list-detail table #test-headers").html(html);
                    $("div#list-detail table #test-body").html(data.msg.body);
                    if(data.msg.crypt != 'none'){
                        $("div#list-detail table #test-crypt").html(data.msg.crypt);
                    }else{
                        $("div#list-detail table #test-crypt").html("无");
                    }
                    if(data.msg.encrypt_content != ""){
                        $("div#list-detail table #test-encrypt_content").html(data.msg.encrypt_content);
                    }else{
                        $("div#list-detail table #test-encrypt_content").html("全部");
                    }
                    if(data.msg.decrypt_content != ""){
                        $("div#list-detail table #test-decrypt_content").html(data.msg.decrypt_content);
                    }else{
                        $("div#list-detail table #test-decrypt_content").html("全部");
                    }
                    var html = "", correlation = data.msg.correlation.split("|");
                    for(var i in correlation){
                        html += correlation[i] + "<br>";
                    }
                    $("div#list-detail table #test-correlation").html(html);
                    var html = "", checkpoint = data.msg.checkpoint.split("|");
                    for(var i in checkpoint){
                        html += checkpoint[i] + "<br>";
                    }
                    $("div#list-detail table #test-checkpoint").html(html);
                    var html = "", check_key = data.msg.check_key.split("\r\n");
                    for(var i in check_key){
                        html += check_key[i] + "<br>";
                    }
                    $("div#list-detail table #test-check_key").html(html);
                    $("div#list-detail table #test-comment").html(data.msg.comment);
                }else{
                    $("div#list-detail table").html(data.msg);
                }
                $("div#list-detail").show("slow", function(){
                    $("#sidebar, nav, .breadcrumb, form").click(function(){
                        $("div#list-detail").hide("slow");
                    });
                });
            }).error(function(data){
                if(data.status == 403){
                    $("#tips-error #tips-error-msg").html("登录超时, 请重新登录!");
                    $("#tips-error").modal();
                    return
                }
            });
        });
    });
    //查看测试详细报告
    $(".report-list").click(function(){
        $("#report-list #reportLabel").text($(this).attr("data-name") + ' 测试报告');
        $("#report-list").modal();
    });
    //立即执行批量接口测试
    $("#list-form .run-list-test").click(function(){
        var $form = $("#list-form"),
            type = $(this).attr("data-type"),
            url = $form.attr("action") + '/runtest';
        $.post(url, $form.serialize() + '&type=' + type, function(data){
            if(data.result){
                location.href = data.msg;
            }else{
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
    });
    //立即执行计划中的任务
    $(".table-responsive .run-job").click(function(){
        var $form = $(".table-responsive #form-jobs-list"),
            url = $form.attr("action") + '/runjob';
        $.post(url, {"sid": $(this).attr("data-sid")}, function(data){
            if(data.result){
                location.href = location.href;
            }else{
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
    });
    //终止任务
    $(".table-responsive .cancel-job").click(function(){
        var $form = $(".table-responsive #form-jobs-list"),
            url = $form.attr("action") + '/canceljob',
            sid = $(this).attr("data-sid");
        $("#alert-warning #alert-msg").html("确定要终止此项任务吗?");
        $("#alert-warning").modal();
        $("#alert-ok").unbind().click(function(){
            $.post(url, {"sid": sid}, function(data){
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
    //任务置顶或取消置顶
    $(".table-responsive .up-to-top").click(function(){
        var $form = $(".table-responsive #form-jobs-list"),
            url = $form.attr("action") + '/up',
            sid = $(this).attr("data-sid"),
            top = $(this).attr("data-top");
        $.post(url, {"sid": sid, "top": top}, function(data){
            location.href = location.href;
        }).error(function(data){
            if(data.status == 403){
                $("#tips-error #tips-error-msg").html("登录超时, 请重新登录!");
                $("#tips-error").modal();
                return
            }
        });
    });
    //查看日志操作
    $('#log-detail').on('show.bs.modal', function (e) {
        $('#log-detail #test-logs').html("");
        var ws = $.websocket('ws://' + location.host + '/admin/websocket/weblogs', {
            open: function(){
                this.send('message', 'get_logs');
            },
            close: function(){
                $('#log-detail #test-logs').append('WebSocket closed<br>');
                this.close();
            },
            events: {
                message: function(e){
                    for(i in e.data){
                        $('#log-detail #test-logs').append(e.data[i] + '<br>');
                        var scrollTop = document.body.scrollHeight + $('#log-detail #test-logs').scrollTop();
                        $('#log-detail #test-logs').scrollTop(scrollTop);
                        if(scrollTop > 10800){
                            $('#log-detail #test-logs').html("");
                        }
                    }
                }
            },
            error: function(){
                $('#log-detail #test-logs').html('Connection WebSocket service error<br>');
                this.close();
            }
        });
        $('#log-detail').on('hidden.bs.modal', function(e){
            ws.close();
            $('#log-detail #test-logs').html("");
        });
    })
});