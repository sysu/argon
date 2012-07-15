function isUndefined(variable) {
    return typeof variable == 'undefined' ? true: false;
}


function showWindow(id, url, title, w, h) {

    var n = notify("加载中...");

    var menuobj = $("#" + id);
    
    var fetchContent = function() {
        menuobj.load(url, function() {
            show();
        });
    };
    
    var show = function() {        
        menuobj.dialog({
            width: w,
            height: h,
            open: function(){$('#id-content').focus();}
        });
        n.hide();
    };

    if (!menuobj.length) {
        menuobj = $("<div>");
        menuobj.attr("id", id);
        menuobj.attr("title", title);
        menuobj.data("url", url);
        menuobj.hide();
        menuobj.appendTo("body");
        fetchContent();

    } else if (url != menuobj.data("url")) {
        menuobj.detach();
        menuobj = $("<div>");
        menuobj.attr("id", id);
        menuobj.attr("title", title);
        menuobj.data("url", url);
        menuobj.appendTo("body");
        fetchContent();
    } else {
        show();
    }
}

function confirm(title, msg, callback) {

    var d = $("<div>");
    d.attr("title", title);
    d.html(msg);
    d.dialog({
        buttons : {
            "确认" : function() {
                callback();
                $(this).remove();
            },
            "取消" : function() {
                $(this).remove();
            }
        }
    });

}

//timeout = 0 表示不会消失
function notify(msg, timeout, link) {
    var n = $("#notify");
    if (n.length == 0) {
        n = $('<div>');
        n.attr("id", "notify");
        n.hide();
        n.appendTo("#notify-pane");
    }
    
    if(link) {
        msg = "<a href='"+ link+"'>"+ msg +"</a>";
    }
    n.html(msg);
    n.show();
    n.attr("style", "display: inline;");
    
    var t = isUndefined(timeout) ? 10000 : timeout;
    if(t>0) {
        setTimeout('$("#notify").fadeOut()', t);
    }
    return n;
}

function boardAutoComplete(ele) {
    $.ajax({
	    url: "/a/allboards/",
	    success: function(boards) {
	        availBoards = eval(boards),
	        ele.autocomplete({
                source: availBoards,
                minLength: '2'
	        });
	    }
    });
}


function reloadCurrentPage() {
    $.get(window.location.hash.substring(2), function(response) {
        $("#content-column").html(response);        
    });    
}



/*  定时ajax检查未处理信息 */
function checkall()
{
    
    $.ajax({
        url: "/a/checkall/",
        cache: false,
        success: function(result){        
        if(result == "m") {
            if(!window.location.hash.match("/mail/$"))  {
                $("#has-new-mail").show();
                notify("收到新邮件啦!",10000, "#!/mail/");
            } else $("#has-new-mail").hide();
            return ;
        }
        $("#has-new-mail").hide();//如果没有mail，就把new-mail清掉
        
        if(result == "@") { 
            if(!window.location.hash.match("/message/$"))  {
                $("#has-new-message").show();
                notify("收到@啦！",10000, "#!/message/");
            }  else $("#has-new-message").hide();
            return ;
        }
        
        if(result == "r") { 
            if(!window.location.hash.match("/message/$"))  {
                $("#has-new-message").show();
                notify("有人回复你啦！",10000, "#!/message/");
            }  else $("#has-new-message").hide();
            return ;
        }
        
        if(result == "f") { 
            if(!window.location.hash.match("/message/$"))  {
                $("#has-new-message").show();
                notify("有人加你为好友啦！",10000, "#!/message/");
            }  else $("#has-new-message").hide();
            return ;
        }

        if(result == "b") {
            if(!window.location.hash.match("/message/$"))  {
                $("#has-new-message").show();
                notify("Argo 祝你生日快乐！",10000, "#!/message/");
            }  else $("#has-new-message").hide();
            return ;
        }
        $("#has-new-message").hide();
    
        }
    });
}

/***********首页初始化***************/
function initMain()
{
    
}

/************* 版块列表 ***************/
function renderBoardList() {
    if($("#board-list").length <= 0) {
        return;
    }
    $('#board-list').delegate('li', 'hover', function() {
        // 跳过 header
        if ($(this).hasClass('board-list-header'))
            return;
        $(this).toggleClass("hover");
    });

    $('#board-list .btitle').click(function() {            
        link = '!/' + $('.bfname', this).text() + '/';
        if(def_mode) link += 'topic/';
        window.location.hash = link;
    });
    
    
    
    // 版主
    $('#board-list .bBM').each(function(index) {
        var BM = $(this).text().split(' ')[0];
        if (BM == '版主') return;
        var link = $('<a>').text(BM).attr('href', '/profile/' + BM);
        $(this).html(link);
    });

    //收藏版面
    $('#board-list .add-button').click(function() {
        var id = $(this).attr('id');
        $.get("/a/addfav/"+id, function(resp){
            notify(resp);
            //reloadCurrentPage('/fav/');
        })
    });
}

function initFav()
{
    /* 删除收藏版面 */
    $('#board-list .del-button').click(function() {
        var id = $(this).attr('id');
        $.get("/a/delfav/"+id, function(resp){
            notify(resp);
            reloadCurrentPage();
        })
    });
    /* 添加收藏版面 */
    $('#id_addfav .common-button').click(function() {
        board=$('#id_addfav .inputtext').val();
        $.get('/a/addfav/'+board, function(resp){
            notify(resp);
            reloadCurrentPage();
        });
    });

    var ele = $('#id_addfav .inputtext');
    $.ajax({
        url: "/a/allboards/",
        success: function(boards) {
            availBoards = eval(boards);
            ele.autocomplete({
                source: availBoards
            });
        }
    });
}
/************* 文章列表 ***************/
function renderPostList() {

    $("#markread").click(function(){
        confirm("清除未读标志", "确认清除本版未读标志？", function() {
            $.post("/post/clear/"+currBoard+"/",{ } , function(resp) {
                notify(resp);
                reloadCurrentPage();
            });
        });
    });
    
    $('#post-button').click(function(){
        if(islogin) {
            var win = $('#fwin-post');
            if (win.is(":visible")) {
                win.dialog('close');
            } else {
                showWindow('fwin-post', "/post/new/" + currBoard , "发表文章", 700, 490);
            }
        } else {            
            showWindow('fwin-login', "/login/", "用户登录", 440, 220);
            notify("请先登录");
        }
    });
    
    
}


/************* 同主题阅读 ***************/

function runover(index, post_name, post_title, content_digest)
{
    var content;
    if(index == Share.length) return ;
    var t = Share[index];
    t.url = t.url.replace("%url%", encodeURIComponent(window.location.href.replace("/t/","/")));
    
    /* change the content according to different sites */
    if(Share[index].type == "sina") {
        if(content_digest.length>0)
            content = '#' + post_title + '# ' + content_digest;
        else content = post_title; 
    } else if (Share[index].type == "renren") {
        content = post_title;
    } else  if (Share[index].type == "qq") {
        content =  '#' + post_title + '# ' + content_digest;
    }  else if(Share[index].type == 'douban'){
        content = post_title;
    }
    
    t.url = t.url.replace("%content%", encodeURIComponent(content));
    $("#share-"+t.type+"-"+post_name).click(function() {
        window.open(t.url, "_blank", 'width=640,height=480');
    });
    runover(index+1, post_name, post_title, content_digest);
}

function share_button(post_name, post_title, content_digest)
{
    Share = [          
        {"type":"sina","url":"http://service.t.sina.com.cn/share/share.php?url=%url%&title=%content%&pic=&appkey=481646317&ralateUid="},
        {"type":"renren","url":"http://www.connect.renren.com/share/sharer?url=%url%&title=%content%"},
        {"type":"qq","url":"http://v.t.qq.com/share/share.php?url=%url%&title=%content%&appkey=e1f12b035c4245e1b3da9a9841c17fe1&site=http://bbs.sysu.edu.cn"},
        {"type":"douban","url":"http://www.douban.com/recommend/?url=%url%&title=%content%"}
    ];
    //,{"title":"分享到腾讯微博","url":"http://v.t.qq.com/share/share.php?url=%url%&title=%content%&appkey=185c1394b1bc4fdd905cdf3ca861b366&site=http://www.newsmth.net","img":'http://v.t.qq.com/share/images/s/weiboicon16.png'},{"title":"分享到搜狐微博","url":"http://t.sohu.com/third/post.jsp?url=%url%&title=%content%&content=utf-8","img":'http://s2.cr.itc.cn/img/t/152.png'},,{"title":"分享到开心网","url":"http://www.kaixin001.com/repaste/bshare.php?rurl=%url%&rtitle=%content%","img":'http://img1.kaixin001.com.cn/i3/platform/ico_kx16.gif'},{"title":"分享到豆瓣","url":"http://www.douban.com/recommend/?url=%url%&title=%content%","img":'http://img2.douban.com/pics/fw2douban_s.png'}];
    
    runover(0, post_name, post_title, content_digest);   

    $("#share-text-"+post_name).hover(function(){
        $("#share-row-"+post_name).toggle("middle");
    });

}


function appendPost(index,data,board,value)
{
    var indexname = ['楼主', '沙发', '板凳', '地板', '地下室', '地壳', '地幔', '地核', '穿越'];
    
    var showuser = function(event) {
	    var win = $('#fwin-query');
	    if (win.is(":visible")) {
            win.dialog('close');
	    } else {
            showWindow('fwin-query', "/profile/query/"+useridArray[index]+"/" , useridArray[index]+" 的资料", 400, 180, event.pageX - document.body.scrollLeft , event.pageY - document.body.scrollTop);                
	    }
    };

    var nodotval = value.replace(/\./g,"-");
    
    $("#"+useridArray[index]+"-"+nodotval).click(function() {
        var win = $('#fwin-query');
        if (win.is(":visible"))  win.dialog('close');
    });

    $("#read-wrap").append($(data).linkify());
    //$("#read-wrap").append(data);

    $("#post-index-"+nodotval).html(index < indexname.length? indexname[index]: index+'楼');

    if(need_to_hide) {
        $(".thread").hide();
        $(".expand-button").hide();
        $(".post-dir-button").hide();
    }
    
    /* 附件图片大小限制 */
    $('.attach_picture').load(function(){
        if($(this).width()>570) $(this).width("570");
    });
    
}

function read_next(index) {
    currIndex = index;
    if(index >= topicFiles.length) {
        var read_more = $("#read-more");
        read_more.hide();
        return ;
    }
    if(index >= nextBound) {
        nextBound = nextBound + loadStep;
        var read_more = $("#read-more");
        read_more.show();
        return ;
    }
    $.ajax({
        url: "/a/" + currBoard + "/" + topicFiles[index],
        success: function(data) {
            appendPost(index, data, currBoard, topicFiles[index], need_to_hide);
            setTimeout("read_next(" + (index + 1) + ", " + need_to_hide + ")", 0);
            //setTimeout("read_next(" + (index + 1) + ")", 0);
        }
    });
}

function readPost(index) {

    topicFiles = isUndefined(topicFiles) ? [] : topicFiles;
    var read_wrap = $("#read-wrap");

    var parsefilename = function(ele, startpos) {
	    var id = $(ele).attr("id");
	    var filename = id.substring(startpos);
	    return filename.replace(/-/g,".");
    };

    var replypost = function(board, value) {
	    var win = $('#fwin-post');
	    if (win.is(":visible")) {
            win.dialog('close');
	    } else {
            showWindow('fwin-post', "/post/reply/" + board + "/"+value, "回复文章", 700, 490);
	    }        
    };

    var editpost = function(board, value) {
	    var win = $('#fwin-post');
	    if (win.is(":visible")) {
            win.dialog('close');
	    } else {
            showWindow('fwin-post', "/post/edit/" + board + "/"+value, "修改文章", 700, 490);
	    }
    };
    
    var copypost = function(board, value){
	    var win = $('#fwin-copy');
	    if (win.is(":visible")) {
            win.dialog('close');
	    } else {
            showWindow('fwin-copy', "/post/copy/" + board + "/"+value, "转载文章", 180, 110);
	    }
    };

    var delpost = function(board, value){
	    confirm("删除文章", "确认删除所选文章？", function() {
            $.post("/post/del/"+board+"/"+value+"/",{ 'board':board, 'filename':value } , function(resp) {
		        notify(resp);
		        reloadCurrentPage();
            });
	    });
    };
    //上篇 下篇
    var readnext = function(board, value) {
        $.get("/a/n/"+board+"/"+value+"/", function(resp) {
            if(resp == 'null' || value == resp ) notify('最后一篇啦～');
            else  {                
                window.location.hash = "!/" + board + "/" + resp;
            }
        });
    };
    var readprev = function(board, value) {
        $.get("/a/p/"+board+"/"+value+"/", function(resp) {
            if(resp == 'null' || value == resp ) notify('已经是第一篇啦～');
            else  {
                window.location.hash = "!/" + board + "/" + resp;
            }
        });
    };
    //推荐到首页的文章
    var recom = function(board, value) {
        var win = $('#fwin-recom');
	    if (win.is(":visible")) {
            win.dialog('close');
	    } else {
            showWindow('fwin-recom', "/recom/" + board + "/"+value+"/", "推荐文章到首页", 280, 210);
	    }
    };
    //查看更多 
    $("#read-more").click(function () {
        $(this).hide();
        read_next(currIndex);
    });

    //从该帖开始展开后面的帖子
    var expand_post = function(board, value) {
        $(this).hide(); //先隐藏，以免重复载入
        $.post("/a/t/"+board+"/"+value+"/", {}, function(files){  //先获取同主题帖子
            topicFiles = files.split("&")[0].split(":");
            useridArray = files.split("&")[1].split(":"); //分离            
            //找到位置并展开
            for(index=0; index<topicFiles.length; index++)
                if(topicFiles[index] == value) {
                    if(index +1 == topicFiles.length) {
                        notify("这是本主题最后一篇啦！");
                    } else  {
                        need_to_hide = 1;
                        nextBound = index + loadStep;
                        read_next(index+1);
                    }
                    break;
                }
        });
    };

    read_wrap.delegate("a[id^='copy']", "click", function(event) {
        event.stopPropagation();
        copypost(currBoard, parsefilename(this, 5));
    });
    read_wrap.delegate("a[id^='del']", "click", function(event) {
        event.stopPropagation();
        delpost(currBoard, parsefilename(this, 4));
    });
    read_wrap.delegate("a[id^='edit']", "click", function(event) {
        event.stopPropagation();
        editpost(currBoard, parsefilename(this, 5));
    });
    read_wrap.delegate("a[id^='reply']", "click", function(event) {
        event.stopPropagation();
        if(islogin)  replypost(currBoard, parsefilename(this, 6));
        else { //未登录show个登录框出来
            showWindow('fwin-login', "/login/", "用户登录", 440, 220);
            notify("请先登录");
        }
    });
    read_wrap.delegate(".post-dir-button[id^='next-post']", "click", function(event) {
        event.stopPropagation();
        readnext(currBoard, parsefilename(this, 10));
    });
    read_wrap.delegate(".post-dir-button[id^='prev-post']", "click", function(event) {
        event.stopPropagation();
        readprev(currBoard, parsefilename(this, 10));
    });
    read_wrap.delegate("a[id^='recom']", "click", function(event) {
        event.stopPropagation();
        recom(currBoard, parsefilename(this, 6));
    });
    read_wrap.delegate("a[id^='expand']", "click", function(event) {
        event.stopPropagation();
        expand_post(currBoard, parsefilename(this, 7));
    });
    //测试快捷键,pageUp读上一帖，pageDown读下一贴
    /*if(window.location.hash.match("/t/") == null ) { //单贴模式
        document.onkeydown = function(e) {
            var currKey=0,e=e||event;
            currKey=e.keyCode||e.which||e.charCode;
            if(currKey == 34) {
                .post-dir-button
            }
        }
    } */
    if(window.location.hash.match("/t/"))  need_to_hide = 1;
    currIndex = 0;
    nextBound = currIndex + loadStep;
    read_next(index);
}


function ajaxPostForm(command, articleid) 
{
    /* 上传附件 */    
    $("#upload-file").hide();
    $("#upload-filename").hide();
    $("#upload-button").click(function(){
        $("#upload-file").width(0);
        $("#upload-file").show();
    });
    $("#upload-file").change(function(event){
        filename=$(this).val();
        last_index = filename.lastIndexOf("\\");
        filename = filename.substr(last_index+1);
        $("#upload-filename").html(filename);
        $("#upload-filename").show();

    });

    
    
    /* 转贴 */
    $("#copy-form").ajaxForm({
        success:function(resp) {
            $('#fwin-copy').dialog('close');
            notify(resp);
            // reloadCurrentPage();
        }
    });

    /* 设定快速提交，由于ie/ff的不兼容性，采取记录相邻
     两次按键，lastKey在post_form.html为全局变量和currKey配合判断
    */ 
    function keyDown(e) {
        var currKey=0,e=e||event;
        currKey=e.keyCode||e.which||e.charCode;
        if(lastKey == 17 && currKey == 13) // enter---13 , x---88
            $('#post-form').submit();
        lastKey = currKey;
    }
    $('#post-form').keydown(keyDown);


    $("#post-form").ajaxForm({
        success:function(resp) {
            $('#fwin-post').dialog('close');
            notify(resp);
            /* 若是文章列表则重载页面 */
            var pattern = /M\.\d{9,10}\.A\/*$/;
            if(!pattern.exec(window.location.hash)) {
                reloadCurrentPage();
                return ;
            }
            if(window.location.hash.match("/t/")!=null || need_to_hide) { //need to hide 为1表示不是单个帖子模式 
                if(command != "reply") {
                    reloadCurrentPage();
                } else {
                    /* 纯发帖则只需要更新最新增加的即可， 不必把之前的载入进来。 */
                    $.post("/a/t/"+currBoard+"/"+articleid+"/", {}, function(files){ 
                        farr = files.split("&")[0].split(":");
                        uarr= files.split("&")[1].split(":");
                        if(farr.length <= topicFiles.length) {
                            reloadCurrentPage();
                        } else {
                            index = topicFiles.length;
                            topicFiles = farr;
                            useridArray = uarr;
                            need_to_hide = 1;
                            read_next(index);
                        }
                    });
                }
            }            
        }
    });    
}

function ajaxRecomForm()
{
    $("#recommend-form").ajaxForm({
        success: function(resp) {
            notify(resp);
            $('#fwin-recom').dialog("close");
        }
    });
}

/***************注册信息***************/

function validate_birthday(y,m,d) //验证是否合法的生日
{
    mon=[31,28,31,30,31,30,31,31,30,31,30,31];
    year = parseInt(y);
    month = parseInt(m);
    day = parseInt(d);
    if(year< 1900 || year > 2012) return false;
    if(month < 1 || month > 12) return false;
    if((year % 4 == 0 && year % 100 !=0) || year % 400 == 0) 
        mon[1]++;
    if(day<1 || day > mon[month-1]) return false;
    return true;
}

function validate_and_ajax_register_form()
{
   register_form = $("#register-form");
   register_submit = $("#register-submit");

   register_submit.click(function() {
       userid = $("#userid").val();
       pass1 = $("#pass1").val();
       pass2 = $("#pass2").val();
       username = $("#username").val();
       realname = $("#realname").val();
       dept = $("#dept").val();
       address = $("#address").val();
       year = $("#year").val();
       month = $("#month").val();
       day = $("#day").val();
       gender = $("#gender").val();
       email = $("#email").val();


       //用户名
       if (userid.length<2 || userid.length>12) {
           notify("用户名长度错误(2-12个英文字符）");
           return ;
       }
       reg = /^[a-zA-Z]*$/;
       if(reg.exec(userid) != userid) {
           notify("用户名只能由英文字母组成"); 
           return ;
       }
       //密码
       if(pass1 == '') {
           notify("密码不能为空");
           return ;
       }
       if(pass1.length<4 || pass1.length>12) {
           notify("密码长度太短(4-12个字符)");
           return ;
       }
       if(pass1 != pass2) {
           notify("两次密码不一致，请重新输入");
           return ;
       }

       //真实姓名，不验证是否中文了= =
       if(realname.length < 2) {
           notify("真实姓名至少2个字");
           return ;
       }

       if(!validate_birthday(year,month,day)) {
           notify("不合法的出生日期");
           return ;
       }
       reg = /\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*?/;
       r_email = reg.exec(email);
       if (!r_email || r_email[0] != email) {
           notify("请输入合法email地址");
           return ;
       }
       //检查是否有人已经注册此帐号
       var exist = 0;
       notifyObj = notify("正在提交注册信息...");
       $.ajax({
          async: false,
          url: "/a/reg/"+userid, 
          success: function(resp) {
               if(resp == 'exist') {
                   notify("此帐号已被注册,请用其他的帐号名。");
                   exist = 1;
                   return ;
               }
           }
       }); 
       if(exist) return ;
       register_form.submit();
       notifyObj.fadeOut(); 
   });   
}

/***************校友验证****************/

function ajax_confirm_info()
{
    $("#select-year").change(function() {

        notifyObj = notify("载入资料中...");
        
        year = $("#select-year").val();
        if(year == "") return ; 
        
        $.get("/a/confirm/"+year+"/", function(resp) {
            notifyObj.fadeOut();
            $("#confirm-info-column").html(resp);
        });

    });
}

function ajax_confirm_info_form()
{
    $("#confirm-info-form").ajaxForm({
        success:function(resp) {
            try_time += 1;
            if(resp == 'yes') {
                alert("验证成功!");
                window.location.href = "/main/";
            } else {
                if(try_time >= 3) {
                    alert("无法验证信息，请联系管理员jmf");
                } else {
                    notify(resp);
                }
            }
        }
    });

}

/***************用户设置***************/

function initSetting()
{
    
    setting_wrap = $("#setting-column");
    setting_wrap.delegate("li[id^='setting']", "click", function(event) {
        event.stopPropagation();
        type = $(this).attr("id").substr(8);
	console.log("hello");
        $.get("/profile/setting/"+type+"/", function(resp) {
            $('#setting-content').html(resp);
        }); 
    });
}
function ajaxSettingSubmit()
{
    $("#setting-content form").ajaxSubmit({
        success:function(resp) {
            notify(resp);
            reloadCurrentPage();
        }
    });
}
//查询用户信息时的js
function  profile_init()
{
    $("#profile-bottom").delegate("div[id^='add']",'click',function(){
        type = $(this).attr('id').substr(4, 6);
        who = $(this).attr('id').substr(11);
        $.post("/profile/add"+type+"/"+ "",{'userid': who} , function(resp){
            notify(resp);
            reloadSettingPage("/profile/setting/"+type+"s/");
        });
    });
    
    $("#write-mail").click(function(){
        var win = $('#fwin-mail');
        if (win.is(":visible")) {
            win.dialog('close');
        } else {
            showWindow('fwin-mail', "/mail/send/" , "写新信件", 480, 350);
        }
    });
}

/************* 加减好友 / 坏人 ***************/

function override_list_init(userid)
{
    var reloadSettingPage = function(path){
        $.get(path ,function(res){
            $("#setting-content").html(res);
        });  
    }
    
    $("#override-bottom .common-button").click(function(event){
        event.stopPropagation();
        type = $(this).attr("id").substr(4);
        who = $("#override-bottom .inputtext").val();
        $.post("/profile/add"+type+"/"+ "",{'userid': who} , function(resp){
            notify(resp);
            reloadSettingPage("/profile/setting/"+type+"s/");
            reloadCurrentPage();
        });
    });

    $("#override-setting").delegate("a[^='del']","click", function(){
        type = $(this).attr("class").substr(4);
        who = $(this).attr("id");
        if(type == "friend") say = "好友";
        else say = "坏人";            
        confirm("删除"+say, "确认删除该"+say+"?", function() {
            $.post("/profile/del"+type+"/",{ 'userid' : who } , function(resp) {
                notify(resp);
                reloadSettingPage("/profile/setting/"+type+"s/");
                reloadCurrentPage();
            });
        });
    });              
    
    $("#override-setting .over-list").hover(function(){
        $(this).toggleClass("hover");
    }); 

}
function ajaxFriendForm(which)
{
    $("#"+which+"-form").ajaxForm({
        success:function(resp) {
            $('#fwin-'+which).dialog('close');
            notify(resp);
            reloadCurrentPage();
        }
    });
}

/************** 好友动态 ********************/
function initOnlineFriend()
{
    //快速回复
    var parsefilename = function(ele, startpos) {
        var id = $(ele).attr("id");
        var filename = id.substring(startpos);
        return filename.replace(/-/g,".");
    };

    var replypost = function(board, value) {
        var win = $('#fwin-post');
        if (win.is(":visible")) {
            win.dialog('close');
        } else {
            showWindow('fwin-post', "/post/reply/" + board + "/"+value, "回复文章", 700, 490);
        }        
    };

    $("#online-friend").delegate("a[id^='reply']", "click", function(event) {
        event.stopPropagation();
        replypost($(this).attr("board"), parsefilename(this, 6));
    });

}

/************* 附件管理 ***************/
function initAttach()
{
    // check or uncheck all
    var toggleCheck = function() {
        if (this.checked) {
            $("#attach-table input:checkbox").prop("checked", true);
        } else {
            $("#attach-table input:checkbox").prop("checked", false);
        }
    }

    // get indexes of checked attach
    var getChecked = function() {
        var checkedObjs = $("#attach-table input:checked");
        if (checkedObjs.length <= 0) {
            notify("请选择附件！", 1500);
            return null;
        }
        var vals = [];
        checkedObjs.each(function() {
            vals.push($(this).val());
        });
        return vals;
    }

    // delete
    var delAttach = function() {
        var checked = getChecked();
        if (checked == null) {
            return;
        }
        confirm("删除附件", "确认删除所选附件？", function() {
            $.post("/attach/del/", { 'indexes[]': checked }, function(resp) {
                notify(resp);
                reloadCurrentPage();
            });
        });
    }
    /* 切换页面 */
    var switchPage = function() {
        var start = $(this).attr("jump");
        if (start != -1) {
            window.location.hash = "#!/attach/list/" + start + "/";
        }
    }
    
    $("#upload-attach").click(function(){
        var win = $('#fwin-upload');
        if (win.is(":visible")) {
            win.dialog('close');
        } else {
            showWindow('fwin-upload', "/attach/upload/" , "上传附件", 262, 150);
        }
    });
    
    $("#upload-attach").hover(function() {
        $("#attach-notify").toggle("middle");
    });
    
    $("#attach-table .attach-body tr").hover(function() {
        $(this).toggleClass("hover");
    }); 

    $("#attach-checkall input:checkbox").click(toggleCheck);
    $("#attach-delete").click(delAttach);
    
    $("#attach-prev").click(switchPage);
    $("#attach-next").click(switchPage);
}

function ajaxUploadForm()
{
    $("#upload-form").ajaxForm({
        success:function(resp) {
            $('#fwin-upload').dialog('close');
            notify(resp);
            reloadCurrentPage();
        }
    });
}

/***********@提到我的************/

function message_init()
{
    var feed_wrap = $("#feed-wrap");

    var parsefilename = function(ele, startpos) {
        var id = $(ele).attr("id");
        var filename = id.substring(startpos);
        return filename.replace(/-/g,".");
    };
    feed_wrap.delegate("a[id^='message']", "click", function(event) {
        event.stopPropagation();
        index = parsefilename(this, 8);
        $.get("/a/message/markread/"+index+"/", function(resp) {
        });
    });
}
function check_message()
{
    $.get("/a/message/check/", function(result){
        if(result == '1'  && !window.location.hash.match("/message/$"))  {
            $("#has-new-message").show();
            notify("收到@啦！",10000, "/message/");
        }  else $("#has-new-message").hide();
    });
}

/************* 邮件 ***************/
function register_read_mail(idx)
{
    var readMail = 
        $("#mail-entry-"+idx).click(function(){
            $(this).removeClass("mail-new");
            var win = $('#fwin-mail');
            if (win.is(":visible")) {
                win.dialog('close');
                reloadCurrentPage();
            } else {
                showWindow('fwin-mail', '/mail/read/'+idx+'/' , '读取信件', 480, 350);
            }
        });       
}
function register_reply_mail(idx)
{
    var replyMail = function() {
	    var win = $('#fwin-mail');
        win.dialog('close');
        showWindow('fwin-mail', '/mail/send/'+idx+'/' , '回复信件', 480, 350);
    }
    $("#reply-mail-"+idx).click(replyMail);
    $(".common-button").hover(function() {
        $(this).toggleClass("button-hover");
    });
}

function initMailControl() {

    // check or uncheck all
    var toggleCheck = function() {
        if (this.checked) {
            $("#mail-table input:checkbox").prop("checked", true);
        } else {
            $("#mail-table input:checkbox").prop("checked", false);
        }
    }

    // get indexes of checked mail
    var getChecked = function() {
        var checkedObjs = $("#mail-table input:checked");
        if (checkedObjs.length <= 0) {
            notify("请选择邮件！", 1500);
            return null;
        }
        var vals = [];
        checkedObjs.each(function() {
            vals.push($(this).val());
        });
        return vals;
    }

    // delete
    var delMail = function() {
        var checked = getChecked();
        if (checked == null) {
            return;
        }
        confirm('删除邮件', '确认删除所选邮件?', function() {
            $.post("/mail/del/", { 'indexes[]': checked }, function(resp) {
                notify(resp);
                reloadCurrentPage();
            });
        });
    }

    // merge
    var mergeMail = function() {
        var checked = getChecked();
        if (checked == null) {
            return;
        }
        confirm("合集邮件", "确认将所选邮件合并为同一封？", function() {
            $.post("/mail/merge/", { 'indexes[]': checked }, function(resp) {
                notify(resp);
                reloadCurrentPage();
            });
        });

    }

    // mark as read
    var markRead = function() {
        var checked = getChecked();
        if (checked == null) {
            return;
        }

        if (true) {
            $.post("/mail/markread/", { 'indexes[]': checked }, function(resp) {
                notify(resp);
                reloadCurrentPage();
            });
        }
    }

    // page switch
    var switchPage = function() {
        var start = $(this).attr("jump");
        if (start != -1) {
            window.location.hash = "#!/mail/" + start + "/";
        }
    }

    //write new mail
    var writeMail = function() {
        var win = $('#fwin-mail');
        if (win.is(":visible")) {
            win.dialog('close');
        } else {
            showWindow('fwin-mail', "/mail/send/" , "写新信件", 480, 350);
        }
    }
    
    
    mail_list = isUndefined(mail_list) ? [] : mail_list;
    for (i = 0; i < mail_list.length; i++)
    {
        register_read_mail(mail_list[i]);
    }
        

    $("#mail-checkall input:checkbox").click(toggleCheck);
    $("#mail-delete").click(delMail);
    $("#mail-merge").click(mergeMail);
    $("#mail-markread").click(markRead);

    $("#mail-prev").click(switchPage);
    $("#mail-next").click(switchPage);
    
    $("#write-mail").click(writeMail);
}

function ajaxMailForm()
{
    $("#mail-form").ajaxForm({
        success:function(resp) {
            $('#fwin-mail').dialog('close');
            notify(resp);
            reloadCurrentPage();
        }
    });
}


/*************** Wiki ******************/

function initWiki(wiki_name)
{
    var wiki_tab = $("#wiki-tabs");

    var parsefilename = function(ele, startpos) {
	    var id = $(ele).attr("id");
	    var filename = id.substring(startpos);
        return filename;
    };

    var editwiki = function(wiki_name, filename) {
        var win = $('#fwin-wiki');
	    if (win.is(":visible")) {
            win.dialog('close');
	    } else {
            showWindow('fwin-wiki', "/" + wiki_name + "/"+filename, "修改内容", 720, 580);
	    }
    }
    wiki_tab.delegate("a[id^='edit']", "click", function(event) {
        event.stopPropagation();        
        editwiki(wiki_name, parsefilename(this, 5));
    });
}

function ajaxWikiForm()
{
    $("#wiki-form").ajaxForm({
        success:function(resp) {
            $('#fwin-wiki').dialog('close');
            notify(resp);
            reloadCurrentPage();
        }
    });
}
