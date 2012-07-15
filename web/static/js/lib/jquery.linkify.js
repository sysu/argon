// simple jquery linkify plugin for argo

(function($){

    var urls = [

	[/&/g, '&amp;'],
	[/</g, '&lt;'],
	[/>/g, '&gt;'],

	// 1. jpg|png|gif pic to <img> tag, class from link
	[/(|\s)(http:\/\/.+?\.)(jpg|png|gif)(\s|$)/g, '$1<img src="$2$3" class="fromlink attach_picture" alt="" />'],
	[/(http:\/\/.+\.)(mp3)/g, '<audio src="$1$2" controls="controls" />'],

	// 2. (http://)v.youku.com... to <embed> tag
	[/(^|\s)(http:\/\/)?v\.youku\.com\/v_show\/id_(\w+)\.html(\s|$)/g,
	 '$1<embed wmode="opaque" src="http://player.youku.com/player.php/sid/$3/v.swf" allowFullScreen="true" quality="high" width="480" height="400" align="middle" allowScriptAccess="always" type="application/x-shockwave-flash"></embed>'],

	// to be added
	// n - 1, url without proto to <a> tag
	[/(^|\s)(www\..+?\..+?)(\s|$)/g,		'$1<a href="http://$2">$2</a>$3'],
	// n, url to <a> tag
	[/(^|\s)(((https?|ftp):\/\/).+?)(\s|$)/g,	'$1<a href="$2">$2</a>$5'],
        //@gcc
	[/@([a-zA-Z]{2,12})/g,	'<a href="/profile/query/$1/">@$1</a>'],
    ];


    linkifyThis = function () {
        var childNodes = this.childNodes,
        i = childNodes.length;
        while(i--) {
            var n = childNodes[i];
	    // 简单将灰色字体的行（<font class="c30">: ...</font>）当作引用，不对引用进行过滤。
	    if ($(n).hasClass("c30"))
		continue;
            if (n.nodeType == 3) {
		var html = $.trim(n.nodeValue);
		if (html)
		{
		    for (u in urls) {
		    	html = html.replace(urls[u][0], urls[u][1]);
		    }
		    $(n).after(html).remove();
		}
            }
            else if (n.nodeType == 1  &&  !/^(a|button|textarea)$/i.test(n.tagName)) {
		linkifyThis.call(n);
            }
        }
    };

    $.fn.linkify = function () {
	return this.each(linkifyThis);
    };

})(jQuery);
