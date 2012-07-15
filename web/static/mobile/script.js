/******* basic *******/

function setCookie(c_name, value, expiredays)
{
    var exdate = new Date();
    exdate.setDate(exdate.getDate() + expiredays);
    document.cookie = c_name + "=" + escape(value) + ";path=/m/" + 
	((expiredays == null) ? "" : ";expires=" + exdate.toGMTString());
}

function eraseCookie(name) {
    setCookie(name,"",-1);
}

function getCookie(c_name)
{
    if (document.cookie.length > 0)
    {
	c_start = document.cookie.indexOf(c_name + "=");
	if (c_start != -1)
	{ 
	    c_start = c_start + c_name.length + 1;
	    c_end = document.cookie.indexOf(";",c_start);
	    if (c_end == -1)
		c_end = document.cookie.length;
	    return unescape(document.cookie.substring(c_start,c_end));
	} 
    }
    return "";
}

function to_time_str(seconds)
{
    var timeObj = new Date(seconds * 1000);
    var m_names = new Array("Jan", "Feb", "Mar", "Apr", "May", "Jun",
			    "Jul", "Aug", "Sept", "Oct", "Nov", "Dec");

    var hour = (timeObj.getHours() > 9 ? '' : '0') + timeObj.getHours();
    var min = (timeObj.getMinutes() > 9 ? '' : '0') + timeObj.getMinutes();
    var date = (timeObj.getDate() > 9 ? '' : '0') + timeObj.getDate();
    var mon = m_names[timeObj.getMonth() - 1];

    return hour + ':' + min + ' ' + mon + ' ' + date;

}

function to_top()
{
    if (document.body.scrollTop == 0) {
	return document.documentElement.scrollTop;
    }
    return document.body.scrollTop;
}

/******* end basic *******/

/******* for m_listpost.html *******/

function m_switch_board(d, seccode) {
    var container = document.getElementById('sec-popup');

    // already loaded, just a display toggle
    if (container.innerHTML != '') {
	container.className = (container.className == '') ? 'hidden' : '';
	return;
    }

    var board_list = '<ul>';
    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
	if (req.readyState == 4 /* complete */) {
	    var bl = eval('(' + req.responseText + ')');
	    for(var i = 0; i < bl.length; i++) {
		board_list += '<li onclick="window.location=\'/m/' + bl[i].filename + '\';">' + bl[i].filename + '</li>';
	    }
	    board_list += '</ul>';
	    container.innerHTML = board_list;
	    container.className = '';
	}
    }
    req.open("GET", "/j/board/" + seccode, /* async */ true);
    req.send(/* no params */ null);
}

function m_collapse_post(index) {
    var e = document.getElementById('entry-row-' + index);
    if (e == null) return;
    e.className = e.className.replace('entry-row-expand', 'entry-row-collapse');
}


function m_collapse_all_post() {
    var entries = document.getElementsByClassName("entry-row-expand");
    for(var i = 0; i < entries.length; i++) {
	entries[i].className =
	    entries[i].className.replace('entry-row-expand', 'entry-row-collapse');
    }
}

function m_expand_post(index, board, filename) {

    var entry = document.getElementById('entry-row-' + index);
    // already expand
    if (entry.className.search('entry-row-collapse') == -1) {
	return;
    }
    window.location.hash = "#" + index;
    var content_div = document.getElementById('entry-content-' + index);
    if (content_div.className.search('entry-no-content') == -1) {
	m_collapse_all_post();
	entry.className = entry.className.replace('entry-row-collapse', 'entry-row-expand');
	entry.scrollIntoView(true);
	return;
    }

    // load content using json
    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
	if (req.readyState == 4 /* complete */) {
	    var data_recv = req.responseText;
	    // remove three header lines and signature..
	    // todo: move implementation to php code ?
	    var ret = data_recv.search('发信人.*标&nbsp;&nbsp;题.*发信站');
	    if (ret != -1) {
		var sub_index = data_recv.indexOf('<br /><br />');
		var end_index = data_recv.indexOf('<br />--<br />'); // not lastIndexOf
		if (end_index != -1) {
		    data_recv = '<font>' + data_recv.substring(sub_index + 6, end_index + 8) + '</font>';
		} else {
		    data_recv = '<font>' + data_recv.substring(sub_index + 6);
		}
	    }

	    content_div.className = content_div.className.replace('entry-no-content', 'entry-has-content');
	    content_div.innerHTML = data_recv;
	    m_collapse_all_post();
	    entry.className = entry.className.replace('entry-row-collapse', 'entry-row-expand');
	    // entry.scrollIntoView(); // not work when rendering ?
	    window.scrollBy(0, entry.getBoundingClientRect().top);
	    var title = document.getElementById('entry-title-' + index);
	    title.className = title.className.replace('new-flag', '');
	}
    }
    req.open("GET", "/m/a/" + board + "/" + filename, /* async */ true);
    req.send(/* no params */ null);
}

function m_expand_prev(index) {
    var i = m_entry_index_list.indexOf(index);
    if (i == 0) {
	plink = document.getElementById('prev-link');
	if (plink) {
	    window.location = plink.href + "#" + (--index);
	    return;
	}
	alert('已是本版第一帖了， =。=');
	return;
    }
    m_expand_post(m_entry_index_list[i - 1], m_board, m_entry_file_list[i - 1]);
}

function m_expand_next(index) {
    var i = m_entry_index_list.indexOf(index);
    if (m_entry_index_list.length == i + 1) {
	nlink = document.getElementById('next-link');
	if (nlink) {
	    window.location = nlink.href + "#" + (++index);
	    return;
	}
	alert('已是本版最后一帖了， =。=');
	return;
    }
    m_expand_post(m_entry_index_list[i + 1], m_board, m_entry_file_list[i + 1]);
}

function m_make_bold_new() {
    for (var i = 0; i < m_entry_index_list.length; i++) {
	var entry = document.getElementById('entry-title-' + m_entry_index_list[i]);
	if (m_entry_read_list[i] == false) {
	    entry.className = entry.className + " new-flag";
	}
    }
}

// recent view board
function m_push_recent() {
    var rv = getCookie("recent_visit");
    var rv_list = rv.split(",");
    var rv_idx = rv_list.indexOf(m_board);
    if (rv_idx != -1) {
	rv_list.splice(rv_idx, 1);
    }
    rv_list.unshift(m_board);
    if (rv_list.length > 6) {
	rv_list.pop();
    }
    setCookie("recent_visit", rv_list.join(","));
}


function m_toggle_recent() {
    var rv = getCookie("recent_visit");
    var rv_list = rv.split(",");
    var rv_div = document.getElementById('recent-view');
    if (rv_div.innerHTML != "") {
	rv_div.innerHTML = "";
	return;
    }
    rv_div.innerHTML = "";
    for (i in rv_list) {
	rv_div.innerHTML += '<div class="recent-visit"><a href="/m/' + rv_list[i] + '/">' + rv_list[i] + '</a></div>';
    }
    // not finished..
}


function m_toggle_topten() {
    var tt_div = document.getElementById('topten-view');
    if (tt_div.className == "") {
	tt_div.className = "hidden";
    } else {
	tt_div.className = "";
    }
}


function m_toggle_reply(index) {
    var i = m_entry_index_list.indexOf(index);
    var filename = m_entry_file_list[i];
    var reply_div = document.getElementById('entry-custom-' + index);
    var entry_reply_text = document.getElementById('entry-reply-text-' + index);
    if (!entry_reply_text) {
	return;
    }
    if (reply_div.innerHTML != "") {
	reply_div.innerHTML = "";
	entry_reply_text.innerHTML = "回复此文";
	return;
    }

    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
	if (req.readyState == 4 /* complete */) {

	    data_recv = eval('(' + req.responseText + ')');
	    reply_div.innerHTML = '<textarea rows="5" id="reply-content-' + index + '">\n\n\n' + data_recv + '</textarea>';
	    reply_div.innerHTML += '<input type="button" value="确定" class="reply-submit" onclick="m_do_reply(\'' + index + '\');" />';
	    entry_reply_text.innerHTML = "取消回复";

	}
    }
    req.open("GET", "/j/" + m_board + "/quote/" + filename, /* async */ true);
    req.send(/* no params */ null);
    
}

function m_do_reply(index) {
    var i = m_entry_index_list.indexOf(index);
    var id = m_entry_id_list[i];
    var title_div = document.getElementById("entry-title-" + index);
    var title = title_div.innerText;
    var content_area = document.getElementById("reply-content-" + index);
    var content = content_area.value;
    if (content == "") {
	alert("你没填什么内容啵。");
	return;
    }
    if (title.substr(0, 4) != "Re: " ) {
	title = "Re: " + title;
    }

    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
	if (req.readyState == 4 /* complete */) {
	    reply_div = document.getElementById('entry-info-' + index);
	    if (req.status == 200) {
		if (req.responseText == '1') {
		    reply_div.innerHTML = "回复成功..";
		} else {
		    reply_div.innerHTML = req.responseText;
		}
	    } else {
		reply_div.innerHTML = "未知错误..";
	    }
	    m_toggle_reply(index);
	}
    }
    var arg = 'title=' + escape(encodeURI(title)) + '&content=' + escape(encodeURI(content)) + '&articleid=' + escape(encodeURI(id));
    req.open("POST", "/a/" + m_board + "/post/", /* async */ true);
    req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    req.send(arg);
    
}

function init_listpost() {
    m_push_recent();
    m_make_bold_new();

    // expand the default
    if(window.location.hash) {
	var index = window.location.hash.substr(1);
	var i = m_entry_index_list.indexOf(index);
	if (i >= 0) {
	    m_expand_post(m_entry_index_list[i], m_board, m_entry_file_list[i]);
	}
    }

    // another onblur method for sec-popup
    document.onclick = function(e) {
	var entries = document.getElementById('post-entries');
	var target = e ? e.target : event.srcElement;
	while (target.parentNode) {
	    target = target.parentNode;
	    if (target == entries) {
		container = document.getElementById('sec-popup');
		container.className = 'hidden';
	    }
	}
    }
    

}

function init_brds() {
    var secs = document.getElementsByClassName("sec_title");
    for (i = 0; i < secs.length; i++) {
	secs[i].closed = true;
	secs[i].onclick = function() {
	    if (this.closed) {
		this.className = "sec_title sec_status_open";
		this.nextElementSibling.className = "boards";
		this.closed = false;
	    } else {
		this.className = "sec_title sec_status_close";
		this.nextElementSibling.className = "boards_hidden";
		this.closed = true;
	    }
	}
    }
}

function m_do_subject_reply(index) {
   var id = parseInt(m_files[0].substring(2)); //
   var filetime = parseInt(m_files[index].substring(2));
   var title_id = document.getElementById("subject-title-" + index);
   var title = title_id.innerText;
   var content_area = document.getElementById("reply-content-" + index);
   var content = content_area.value;
  
    if (title.substr(0, 3) != "Re:" ) {
	    title = "Re: " + title;
    }

    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (req.readyState == 4 /* complete */) {
            var reply_div = document.getElementById('subject-custom-'+filetime); 
            reply_div.innerHTML = "";
        }
    }
    var arg = 'title=' + escape(encodeURI(title)) + '&content=' + escape(encodeURI(content)) + '&articleid=' + escape(encodeURI(id));
    req.open("POST", "/a/" + m_board + "/post/", /* async */ true);
    req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    req.send(arg);
}

function m_subject_reply(index) //subject index,start from 0
{
    var filename = m_files[index];
    var filetime = parseInt(filename.substring(2));
    var reply_div = document.getElementById('subject-custom-'+filetime); 

    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if(req.readyState == 4) {
            data_recv = eval('('+ req.responseText +')');
            reply_div.innerHTML = '<textarea rows="5" id="reply-content-' + index + '">\n\n\n' + data_recv + '</textarea>';
            reply_div.innerHTML += '<input type="button" value="确定" class="reply-submit" onclick="m_do_subject_reply(\'' + index + '\');" />';
        }
    }
    req.open("GET", "/j/" + m_board + "/quote/" + filename, /* async */ true);
    req.send(/* no params */ null);

}

function subject_read_next(index) {
    if (index >= m_files.length) {
	var read_more = document.getElementById('subject-more');
	read_more.innerHTML = '';
	read_more.className= '';
	return;
    }

    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
    	if (req.readyState == 4 /* complete */) {

	    var data = req.responseText;
       
	    var ret;
	    ret = data.search("发信人");
	    var author = ret > 0 ? data.substring(ret + 10, data.indexOf('&nbsp;(')) : 'unknown';
	    ret = data.search("标&nbsp;&nbsp;题");
	    var title = ret > 0 ? data.substring(ret + 21, data.indexOf('<br />发信站')) : '未知标题';

	    ret = data.search('发信人.*标&nbsp;&nbsp;题.*发信站');

	    if (ret != -1) {
            var sub_index = data.indexOf('<br /><br />');
            var end_index = data.indexOf('<br />--<br />'); // not lastIndexOf

            if (end_index != -1) {
                data = data.substring(sub_index + 6, end_index + 8);
            } else {
                data = data.substring(sub_index + 6);
            }
	    }

	    var filetime = parseInt(m_files[index].substring(2));

	    var inner_data = '<div class="subject-title" id="subject-title-'+index+'">' + title + '</div>';
	    inner_data += '<div class="subject-author">- ' + author + ', ' + to_time_str(filetime) + '</div>';
	    inner_data += '<div class="subject-content">' + '<font>' + data + '</font></div>';
	    inner_data += '<div class="subject-reply" onclick="javascript:m_subject_reply('+index+')">回复此文</div>';
        inner_data += '<div class="entry-custom" id="subject-custom-'+ filetime +'"></div>';
	    inner_data += '<div class="clear"></div>';
	    var content_div = document.getElementById('content-div');
	    content_div.innerHTML += '<div class="subject-row">' + inner_data + '</div>';
	    
        if((index + 1) % 10) {
            subject_read_next(index + 1);
        } else {
            if (index + 1 >= m_files.length) return;
            var read_more = document.getElementById('subject-more');
            read_more.innerHTML = '阅读更多';
            read_more.className= 'more';
        }
        }
    }
    req.open("GET", "/m/a/" + m_board + "/" + m_files[index], /* async */ true);
    req.send(/* no params */ null);
    
}

function subject_more() {
    var content_div = document.getElementById('content-div');
    var next_index = content_div.childElementCount;
    subject_read_next(next_index);
}

function init_subject_read() {
    subject_read_next(0);
}

function m_collapse_all_mail() {
    var entries = document.getElementsByClassName("mail-entry-expand");
    for(var i = 0; i < entries.length; i++) {
	entries[i].className =
	    entries[i].className.replace('mail-entry-expand', 'mail-entry-collapse');
    }
}

function m_toggle_mail(index) {
    var entry = document.getElementById("mail-entry-" + index);
    var content_div = document.getElementById("mail-content-" + index);

    /* already expand */
    if (entry.className.search('mail-entry-collapse') == -1) {
	entry.className = entry.className.replace('mail-entry-expand', 'mail-entry-collapse');
	return;
    }

    if (content_div.innerHTML != "") {
	m_collapse_all_mail();
    	entry.className = entry.className.replace('mail-entry-collapse', 'mail-entry-expand');
    	entry.scrollIntoView();
	return;
    }

    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
    	if (req.readyState == 4 /* complete */) {

            alert(req.responseText);

   	    var data_recv = eval('(' + req.responseText + ')');
    	    content_div.innerHTML = data_recv;
	        m_collapse_all_mail();
    	    entry.className = entry.className.replace('mail-entry-collapse', 'mail-entry-expand');
	    entry.className = entry.className.replace('mail-new', '');
    	    entry.scrollIntoView();
    	}
    }
    req.open("GET", "/j/mail/" + index, /* async */ true);
    req.send(/* no params */ null);
}

function init_current_nav() {
    var loc_str = window.location + "";
    var loc = loc_str.split("/");
    loc = loc.filter(function(data){return data? true: false;});
    loc = loc[loc.length - 1];
    var nav_list = ['m', 'brds', 'fav', 'mail', 'data', 'about'];
    if (nav_list.indexOf(loc) != -1) {
	document.getElementById("nav-" + loc).className += " selected";
	setCookie("nav", loc);
    } else {
	var nav = getCookie("nav");
	if (nav != "")
	    document.getElementById("nav-" + nav).className += " selected";
    }
}

function check_mail() {
    var nav = document.getElementById('nav-mail');
    if (!nav || nav.className.search('selected') > 0) {
	return;
    }
    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
    	if (req.readyState == 4 /* complete */) {
    	    if (req.responseText == '0') {
    		nav.className = nav.className.replace('mail-unread', 'mail-read');
	    } else {
    		nav.className = nav.className.replace('mail-read', 'mail-unread');
	    }
    	}
    }
    req.open("GET", "/a/checkmail/", /* async */ true);
    req.send(/* no params */ null);
}


function init() {
    init_current_nav();
    check_mail();

    if ((typeof(page_init_code) == 'string')) {
	eval(page_init_code);
    }
    
}

window.onload = init;
