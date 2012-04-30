/*
   对版面帖子进行切表
   一个版一个表
   新建版的时候从此模板render掉 ${boardname} 即可
   后期将加入回收站功能
*/
DROP TABLE IF EXISTS `argo_filehead_${boardname}`;
CREATE TABLE IF NOT EXISTS `argo_filehead_${boardname}` (
    `pid` int(11) unsigned NOT NULL auto_increment,
    `bid` int(11) unsigned NOT NULL, 
    `owner` varchar(14),
    `realowner` varchar(14),
    `title` varchar(60),
    `flag` int(11)  unsigned default 0,
    `tid` int(11) unsigned default 0,
    `replyid` int(11) unsigned,
    `posttime` int(11) unsigned, 
    `attachidx` varchar(20),

    `fromaddr` varchar(64),
    `fromhost` varchar(64) NOT NULL default "Yat-sen Channel",

    `content` text,
    `quote` text,
    `signature` text,
    
    `agree` int(11) unsigned NOT NULL default 0,
    `disagree` int(11) unsigned NOT NULL default 0,
    `credit`  int(11) NOT NULL default 0,

    PRIMARY KEY (`pid`)
) ENGINE=InnoDB  DEFAULT CHARSET=UTF8;


