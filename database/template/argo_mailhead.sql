/*
    tableid = uid / 100
*/
DROP TABLE IF EXISTS `argo_mailhead_${tableid}`;
CREATE TABLE IF NOT EXISTS `argo_mailhead_${tableid}` (
    `mid` int(11) unsigned NOT NULL auto_increment,
    `fromuserid` varchar(16) NOT NULL,
    `touserid` varchar(16) NOT NULL,
    `attachidx` varchar(128),

    `tid` int(11) unsigned ,
    `replyid` int(11) unsigned NOT NULL default 0,
    `title` varchar(60),

    `sendtime` timestamp NOT NULL default CURRENT_TIMESTAMP ,
    `fromaddr` varchar(64),
    
    `readmark` int(11) unsigned NOT NULL default 0,
    `flag` int(11) unsigned NOT NULL default 0,
    `content` text,
    `quote` text,
    `signature` text,

    PRIMARY KEY (`mid`)
) ENGINE=MyISAM DEFAULT CHARSET=UTF8;

