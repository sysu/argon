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
    `posttime` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
    `attachidx` varchar(20),

    `fromaddr` varchar(64),
    `fromhost` varchar(64) NOT NULL default "Yat-sen Channel",

    `content` text,
    `quote` text,
    `signature` text,
    
    `agree` int(11) unsigned NOT NULL default 0,
    `disagree` int(11) unsigned NOT NULL default 0,
    `credit`  int(11) NOT NULL default 0,
    
    `originalfilename` varchar(32), /* M.123456789.A */

    PRIMARY KEY (`pid`)
) ENGINE=InnoDB  DEFAULT CHARSET=UTF8;
