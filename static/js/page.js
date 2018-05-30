$("form#check-link").ready(function(){
    //启动链接检查, 实时查看日志
    var ws = $.websocket('ws://' + location.host + '/admin/websocket/weblogs', {
        close: function(){
            $('form#check-link #check-logs').append('WebSocket closed<br>');
            this.close();
        },
        events: {
            message: function(e){
                for(i in e.data){
                    $('form#check-link #check-logs').append(e.data[i] + '<br>');
                    var scrollTop = document.body.scrollHeight + $(document).scrollTop();
                    $(document).scrollTop(scrollTop);
                    if (scrollTop > 10800){
                        $("form#check-link #check-logs").html("");
                    }
                }
            }
        },
        error: function(){
            $('form#check-link #check-logs').html('Connection WebSocket service error<br>');
            this.close();
        }
    });
    $("form#check-link #check-all").click(function(){
        var value = $("form#check-link #url").val();
        if($(this).is(":checked")){
            value = value.split('\n');
            $("form#check-link #check-url").html('<input id="url" name="url" class="form-control" value="' + value[0] + '">');
        }else{
            $("form#check-link #check-url").html('<textarea id="url" name="url" class="form-control">' + value + '</textarea>');
        }
    });
    $("form#check-link #check-submit").click(function(){
        var $form = $("form#check-link"),
            url = $form.attr("action");
        $("form#check-link #check-logs").html("");
        $("form#check-link #check-result").addClass("sr-only");
        ws.send('message', 'get_logs');
        $.post(url, $form.serialize(), function(data){
            if(!data.result){
                $("form#check-link #check-logs").html(data.msg + '<br><br>');
            }else{
                $("form#check-link #check-result").attr('href', data.msg)
                $("form#check-link #check-result").removeClass("sr-only");
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